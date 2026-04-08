from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ytmusicapi import YTMusic
import pymysql
import auth
from pydantic import BaseModel
from dotenv import load_dotenv
import os


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

yt = YTMusic('browser.json')
load_dotenv()

class LoginData(BaseModel):
    username: str
    password: str

def get_connection():
    return pymysql.connect(
        host=os.getenv("domain"),
        user=os.getenv("username"),
        password=os.getenv("password"),
        database=os.getenv("database"),
        port=int(os.getenv("port", 3306))
    )

@app.get("/api/search")
async def search(query: str):
    search_results = yt.search(query)
    filtered = [
        {
            "videoId": r.get("videoId"),
            "title": r.get("title") or r.get("artist"),
            "artist": r["artists"][0]["name"] if r.get("artists") else None,
            "thumbnail": next((t["url"] for t in r.get("thumbnails", []) if t["width"] == 60), None),
        }
        for r in search_results
    ]
    return {"results": filtered}

@app.get("/api/add")
async def add(videoID: str):
    try:
        song = yt.get_song(videoID)
        yt.add_playlist_items("PLJhSTAItRjxJl8f9mcHenCKVotPkSDFVB", [videoID])
        if not song or not song.get("videoDetails"):
            raise HTTPException(status_code=404, detail="Nie znaleziono piosenki o podanym ID")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Nieprawidłowe ID: {str(e)}")


@app.post("/api/login")
async def login(data: LoginData):
    login_status = auth.login(data.username, data.password)
    if login_status == False:
        raise HTTPException(status_code=401, detail="Błędny login lub hasło")
    return {"token": login_status}


@app.get("/api/list")
async def list(token: str):
    is_auth = auth.auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail="Klucz JWT niepoprawny")

    PLAYLIST_ID = "PLJhSTAItRjxJl8f9mcHenCKVotPkSDFVB"
    try:
        playlist = yt.get_playlist(PLAYLIST_ID, limit=None)
        playlist_tracks = playlist.get("tracks", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd pobierania playlisty: {str(e)}")

    result = []
    for track in playlist_tracks:
        videoID = track.get("videoId")
        thumbnails = track.get("thumbnails") or []
        result.append({
            "videoID": videoID,
            "title": track.get("title"),
            "author": ", ".join(
                a["name"] for a in (track.get("artists") or [])
            ),
            "lengthSeconds": track.get("duration_seconds"),
            "thumbnail": thumbnails[-1].get("url") if thumbnails else None,
            "url": f"https://music.youtube.com/watch?v={videoID}"
        })

    return result


@app.get("/api/delete")
async def decline(token: str, videoID: str):
    is_auth = auth.auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail="Klucz JWT niepoprawny")

    PLAYLIST_ID = "PLJhSTAItRjxJl8f9mcHenCKVotPkSDFVB"

    # Pobierz playlistę żeby znaleźć setVideoId potrzebny do usunięcia
    try:
        playlist = yt.get_playlist(PLAYLIST_ID, limit=None)
        playlist_tracks = playlist.get("tracks", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd pobierania playlisty: {str(e)}")

    # Znajdź utwór po videoId — get_playlist wymaga setVideoId do usunięcia
    track = next(
        (t for t in playlist_tracks if t.get("videoId") == videoID),
        None
    )

    if not track:
        raise HTTPException(status_code=404, detail="Nie znaleziono utworu w playliście")

    set_video_id = track.get("setVideoId")
    if not set_video_id:
        raise HTTPException(status_code=500, detail="Brak setVideoId — nie można usunąć utworu")

    try:
        yt.remove_playlist_items(PLAYLIST_ID, [{"videoId": videoID, "setVideoId": set_video_id}])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd usuwania z playlisty: {str(e)}")

    return {"success": True, "videoID": videoID}
@app.delete("/api/clear-playlist")
async def clear_playlist(token:str):
    is_auth = auth.auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail="Klucz JWT niepoprawny")

    PLAYLIST_ID = "PLJhSTAItRjxJl8f9mcHenCKVotPkSDFVB"
    try:
        playlist = yt.get_playlist(PLAYLIST_ID, limit=None)
        tracks = playlist.get("tracks", [])

        if not tracks:
            return {"message": "Playlista jest już pusta.", "removed": 0}

        yt.remove_playlist_items(PLAYLIST_ID, tracks)

        return {
            "message": "Playlista została wyczyszczona.",
            "removed": len(tracks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
