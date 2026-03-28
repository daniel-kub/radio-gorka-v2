import pymysql
import jwt
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("domain"),
        user=os.getenv("username"),
        password=os.getenv("password"),
        database=os.getenv("database"),
        port=int(os.getenv("port", 3306))
    )
    



def login(username, password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user is None:
            return False
        hashed = user[0].encode("utf-8") if isinstance(user[0], str) else user[0]
        if bcrypt.checkpw(password.encode("utf-8"), hashed):
            token = jwt.encode(
                {"username": username, "password": password},
                "secret",
                algorithm="HS256"
            )
            return token
        return False
    finally:
        conn.close()

def auth(key):
    try:
        data = jwt.decode(key, "secret", algorithms=["HS256"])
    except Exception:
        return False
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (data["username"],))
        user = cursor.fetchone()
        if user is None:
            return False
        hashed = user[0].encode("utf-8") if isinstance(user[0], str) else user[0]
        return bcrypt.checkpw(data["password"].encode("utf-8"), hashed)
    finally:
        conn.close()
