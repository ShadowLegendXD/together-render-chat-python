import datetime
import os
import sqlite3
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import jwt
import socketio

JWT_SECRET = "O5_COUNCIL_CLASSIFIED_KEY_99"
ALGORITHM = "HS256"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
sio_app = socketio.ASGIApp(sio)

DB_FILE = "chat_hub.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # CRITICAL FIX: Changed 'TEXT NOT EXISTS' to 'TEXT NOT NULL'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            active_theme TEXT DEFAULT 'scp'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            text TEXT,
            voice TEXT,
            timestamp TEXT,
            theme_context TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def create_token(username: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    return jwt.encode({"sub": username, "exp": expire}, JWT_SECRET, algorithm=ALGORITHM)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    public_path = os.path.join("public", "index.html")
    if not os.path.exists(public_path):
        raise HTTPException(status_code=404, detail="index.html file not found inside public folder.")
    with open(public_path, "r", encoding="utf-8") as file:
        return file.read()

@app.post("/api/register")
async def register(data: dict):
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="Parameters missing.")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Codename profile already registered.")
    
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    
    token = create_token(username)
    return {"success": True, "token": token, "username": username, "theme": "scp"}

@app.post("/api/login")
async def login(data: dict):
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password, active_theme FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[0] != password:
        raise HTTPException(status_code=401, detail="Invalid clearance access key.")
        
    token = create_token(username)
    return {"success": True, "token": token, "username": username, "theme": row[1]}

@app.get("/api/verify")
async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No terminal token provided.")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload["sub"]
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT active_theme FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        return {"success": True, "username": username, "theme": row[0] if row else "scp"}
    except Exception:
        raise HTTPException(status_code=401, detail="Clearance expired or invalid token.")

@app.post("/api/theme")
async def update_theme(data: dict, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized token verification request.")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload["sub"]
        new_theme = data.get("theme", "scp")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET active_theme = ? WHERE username = ?", (new_theme, username))
        conn.commit()
        conn.close()
        return {"success": True, "theme": new_theme}
    except Exception:
        raise HTTPException(status_code=401, detail="Theme verification error.")

@sio.event
async def join(sid, username):
    await sio.save_session(sid, {"username": username})
    print(f"[COM LINK ACTIVE]: {username}")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, text, voice, timestamp FROM messages ORDER BY id ASC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        await sio.emit("receiveMessage", {
            "sender": row[0],
            "text": row[1],
            "voice": row[2],
            "timestamp": row[3],
            "isHistory": True
        }, room=sid)

@sio.event
async def sendMessage(sid, data):
    session = await sio.get_session(sid)
    username = session.get("username", "Unknown Operator")
    timestamp = datetime.datetime.now().strftime("%I:%M %p")
    text_data = data.get("text")
    voice_data = data.get("voice")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, text, voice, timestamp) VALUES (?, ?, ?, ?)",
                   (username, text_data, voice_data, timestamp))
    conn.commit()
    conn.close()
    
    await sio.emit("receiveMessage", {
        "sender": username,
        "text": text_data,
        "voice": voice_data,
        "timestamp": timestamp
    })

app.mount("/socket.io", sio_app)
