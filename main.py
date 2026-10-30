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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            active_theme TEXT DEFAULT 'scp',
            custom_bg TEXT DEFAULT ''
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT DEFAULT 'Global',
            sender TEXT,
            text TEXT,
            voice TEXT,
            timestamp TEXT
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
        raise HTTPException(status_code=404, detail="index.html not found inside public folder.")
    with open(public_path, "r", encoding="utf-8") as file:
        return file.read()

@app.post("/api/register")
async def register(data: dict):
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing registration parameters.")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Operator username already active.")
    
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return {"success": True, "token": create_token(username), "username": username, "theme": "scp"}

@app.post("/api/login")
async def login(data: dict):
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password, active_theme, custom_bg FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[0] != password:
        raise HTTPException(status_code=401, detail="Access Denied: Invalid clearance access key.")
        
    return {
        "success": True, 
        "token": create_token(username), 
        "username": username, 
        "theme": row[1], 
        "custom_bg": row[2]
    }

@app.get("/api/verify")
async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization signature token.")
    
    token = authorization.split(" ")[1] if " " in authorization else authorization
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload["sub"]
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT active_theme, custom_bg FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        return {"success": True, "username": username, "theme": row[0], "custom_bg": row[1]}
    except Exception:
        raise HTTPException(status_code=401, detail="Session expired.")

@app.get("/api/accounts")
async def list_accounts():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = [r[0] for r in cursor.fetchall()]
    conn.close()
    return {"accounts": users}

@app.post("/api/theme/custom")
async def save_custom_theme(data: dict):
    username = data.get("username")
    bg_data = data.get("bg_data", "")
    theme = data.get("theme", "custom")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET active_theme = ?, custom_bg = ? WHERE username = ?", (theme, bg_data, username))
    conn.commit()
    conn.close()
    return {"success": True}

@sio.event
async def join(sid, data):
    username = data.get("username")
    room = data.get("room", "Global")
    await sio.save_session(sid, {"username": username, "room": room})
    sio.enter_room(sid, room)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, text, voice, timestamp FROM messages WHERE room = ? ORDER BY id ASC LIMIT 50", (room,))
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        await sio.emit("receiveMessage", {
            "sender": row[0], "text": row[1], "voice": row[2], "timestamp": row[3], "isHistory": True
        }, room=sid)

@sio.event
async def sendMessage(sid, data):
    session = await sio.get_session(sid)
    username = session.get("username", "Unknown")
    room = session.get("room", "Global")
    timestamp = datetime.datetime.now().strftime("%I:%M %p")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (room, sender, text, voice, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (room, username, data.get("text"), data.get("voice"), timestamp))
    conn.commit()
    conn.close()
    
    await sio.emit("receiveMessage", {
        "sender": username, "text": data.get("text"), "voice": data.get("voice"), "timestamp": timestamp
    }, room=room)

@sio.event
async def callSignal(sid, data):
    room = data.get("room")
    await sio.emit("receiveSignal", data, room=room, skip_sid=sid)

app.mount("/socket.io", sio_app)
