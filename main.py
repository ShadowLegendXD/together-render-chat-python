import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="SCP Foundation Tactical Hub")

messages_db = [
    {"user": "SYSTEM", "text": "[SECURE. CONTAIN. PROTECT.] Intranet node synchronized.", "time": "00:00:00"}
]

class MessageModel(BaseModel):
    user: str
    text: str

@app.get("/", response_class=HTMLResponse)
async def get_terminal():
    target_path = os.path.join("public", "index.html")
    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    return HTMLResponse(content="<h2>Error: public/index.html is missing.</h2>", status_code=404)

@app.get("/api/history")
async def get_history():
    return messages_db

@app.post("/api/transmit")
async def transmit_message(payload: MessageModel):
    now = datetime.now().strftime("%H:%M:%S")
    messages_db.append({"user": payload.user, "text": payload.text, "time": now})
    return {"status": "TRANSMITTED"}
