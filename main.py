import datetime
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
import jwt
import socketio

# Configuration
JWT_SECRET = "O5_COUNCIL_CLASSIFIED_KEY_99"
ALGORITHM = "HS256"

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO setup (ASGI compatible)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Mock database
users_db = {}

# --- Helper Functions ---
def create_token(username: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    return jwt.encode({"sub": username, "exp": expire}, JWT_SECRET, algorithm=ALGORITHM)

# --- REST Authentication Endpoints ---
@app.post("/api/register")
async def register(data: dict):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing credentials.")
    if username in users_db:
        raise HTTPException(status_code=400, detail="Codename already active.")
    
    users_db[username] = {"password": password}
    token = create_token(username)
    return {"success": True, "token": token, "username": username}

@app.post("/api/login")
async def login(data: dict):
    username = data.get("username")
    password = data.get("password")
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Access Denied. Invalid clearance.")
    
    token = create_token(username)
    return {"success": True, "token": token, "username": username}

@app.get("/api/verify")
async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No terminal token.")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return {"success": True, "username": payload["sub"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Clearance token expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid clearance token.")

# --- Socket.IO Events ---
@sio.event
async def connect(sid, environ):
    print(f"[SECURE LINE ATTEMPT] SID: {sid}")

@sio.event
async def join(sid, username):
    await sio.save_session(sid, {"username": username})
    print(f"[SECURE LINE CONNECTED]: {username}")

@sio.event
async def sendMessage(sid, data):
    session = await sio.get_session(sid)
    username = session.get("username", "Unknown Agent")
    
    # Broadcast voice array strings or texts to all terminals
    await sio.emit("receiveMessage", {
        "sender": username,
        "text": data.get("text"),
        "voice": data.get("voice"),
        "timestamp": datetime.datetime.now().strftime("%I:%M:%S %p")
    })

@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    username = session.get("username", "Unknown Agent")
    print(f"[LINE DISCONNECTED]: {username}")

# Render entry point command target: main:app
app.mount("/", sio_app)
