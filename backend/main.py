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

def get_event_connection():
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
        if not song or not song.get("videoDetails"):
            raise HTTPException(status_code=404, detail="Nie znaleziono piosenki o podanym ID")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Nieprawidłowe ID: {str(e)}")

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT status, reason FROM tracks WHERE videoID = %s", (videoID,))
        row = cursor.fetchone()

        if row is None:
            cursor.execute("INSERT INTO tracks (videoID, status) VALUES (%s, 'check')", (videoID,))
            conn.commit()
            return JSONResponse(status_code=201, content={"result": "inserted", "message": "Piosenka dodana do sprawdzenia"})

        status = row[0]

        if status == "check":
            raise HTTPException(status_code=409, detail="Piosenka jest już oczekująca na sprawdzenie")
        elif status == "accepted":
            raise HTTPException(status_code=409, detail="Piosenka została już zaakceptowana")
        elif status == "declined":
            reason = row[1]
            raise HTTPException(status_code=403, detail=f"Piosenka została odrzucona z powodu: {reason}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


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

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE status='check'")
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    result = []
    for row in rows:
        videoID = row[1]
        try:
            song = yt.get_song(videoID)
            details = song.get("videoDetails", {})
            result.append({
                "videoID": videoID,
                "status": row[2],
                "reason": row[3],
                "title": details.get("title"),
                "author": details.get("author"),
                "lengthSeconds": details.get("lengthSeconds"),
                "viewCount": details.get("viewCount"),
                "thumbnail": details.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url"),
                "url": f"https://music.youtube.com/watch?v={videoID}"
            })
        except Exception:
            result.append({
                "videoID": videoID,
                "status": row["status"],
                "reason": row["reason"],
                "title": None,
                "author": None,
                "lengthSeconds": None,
                "viewCount": None,
                "thumbnail": None,
                "url": f"https://music.youtube.com/watch?v={videoID}"
            })

    return result

@app.get("/api/accept")
async def accept(token: str, videoID: str):
    is_auth = auth.auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail="Klucz JWT niepoprawny")

    try:
        song = yt.get_song(videoID)
        yt.add_playlist_items("PLJhSTAItRjxJl8f9mcHenCKVotPkSDFVB", [videoID])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Nieprawidłowe ID: {str(e)}")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tracks SET status='accepted' WHERE videoID=%s", (videoID,))
        conn.commit()
        return JSONResponse(status_code=204, content={"message": f"Pomyślnie zaakceptowano i dodano {videoID}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/decline")
async def decline(token: str, videoID: str, reason: str):
    is_auth = auth.auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail="Klucz JWT niepoprawny")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tracks SET status='declined', reason=%s WHERE videoID=%s", (reason, videoID))
        conn.commit()
        return JSONResponse(status_code=204, content={"message": f"Pomyślnie odrzucono {videoID}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/event/add")
async def event_add(videoID: str):
    try:
        song = yt.get_song(videoID)
        if not song or not song.get("videoDetails"):
            raise HTTPException(status_code=404, detail="Nie znaleziono piosenki o podanym ID")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Nieprawidłowe ID: {str(e)}")

    conn = get_event_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT status, reason FROM tracks_event WHERE videoID = %s", (videoID,))
        row = cursor.fetchone()

        if row is None:
            cursor.execute("INSERT INTO tracks_event (videoID, status) VALUES (%s, 'check')", (videoID,))
            conn.commit()
            return JSONResponse(status_code=201, content={"result": "inserted", "message": "Piosenka dodana do sprawdzenia"})

        status = row[0]

        if status == "check":
            raise HTTPException(status_code=409, detail="Piosenka jest już oczekująca na sprawdzenie")
        elif status == "accepted":
            raise HTTPException(status_code=409, detail="Piosenka została już zaakceptowana")
        elif status == "declined":
            reason = row[1] or ""
            raise HTTPException(status_code=403, detail=f"Piosenka została odrzucona z powodu: {reason}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/event/list")
async def event_list(token: str):
    is_auth = auth.auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail="Klucz JWT niepoprawny")

    conn = get_event_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks_event WHERE status='check'")
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    result = []
    for row in rows:
        videoID = row[1]
        try:
            song = yt.get_song(videoID)
            details = song.get("videoDetails", {})
            result.append({
                "videoID": videoID,
                "status": row[2],
                "reason": row[3],
                "title": details.get("title"),
                "author": details.get("author"),
                "lengthSeconds": details.get("lengthSeconds"),
                "viewCount": details.get("viewCount"),
                "thumbnail": details.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url"),
                "url": f"https://music.youtube.com/watch?v={videoID}"
            })
        except Exception:
            result.append({
                "videoID": videoID,
                "status": row["status"],
                "reason": row["reason"],
                "title": None,
                "author": None,
                "lengthSeconds": None,
                "viewCount": None,
                "thumbnail": None,
                "url": f"https://music.youtube.com/watch?v={videoID}"
            })

    return result


@app.get("/api/event/accept")
async def event_accept(token: str, videoID: str):
    is_auth = auth.auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail="Klucz JWT niepoprawny")

    try:
        song = yt.get_song(videoID)
        if not song or not song.get("videoDetails"):
            raise HTTPException(status_code=404, detail="Nie znaleziono piosenki o podanym ID")
        yt.add_playlist_items("PLJhSTAItRjxLS10EQ7dNbeUOPcnIW2m6r", [videoID])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Nieprawidłowe ID: {str(e)}")

    conn = get_event_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tracks_event SET status='accepted' WHERE videoID=%s", (videoID,))
        conn.commit()
        return JSONResponse(status_code=204, content={"message": f"Pomyślnie zaakceptowano i dodano {videoID}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.get("/api/event/decline")
async def event_decline(token: str, videoID: str, reason: str):
    is_auth = auth.auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail="Klucz JWT niepoprawny")

    conn = get_event_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tracks_event SET status='declined', reason=%s WHERE videoID=%s", (reason, videoID))
        conn.commit()
        return JSONResponse(status_code=204, content={"message": f"Pomyślnie odrzucono {videoID}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/status")
async def get_status():
    return {
        "name": "Radio Górka"
    }
