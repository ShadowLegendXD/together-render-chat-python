import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="SCP Foundation Tactical Hub")

# Cloud Memory Buffer (Zero PC Storage Used)
messages_db = [
    {"user": "SYSTEM", "text": "[SECURE. CONTAIN. PROTECT.] Network loop operational.", "time": "00:00:00"}
]

class MessageModel(BaseModel):
    user: str
    text: str

@app.get("/", response_class=HTMLResponse)
async def get_terminal():
    # Embedding a clean chat engine straight into the script to bypass missing file errors instantly!
    html_layout = """
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>SCP Foundation</title>
    <style>
        body { background: #07090e; color: #f8f8f2; font-family: monospace; padding: 20px; }
        #log { border: 1px solid #1b2330; height: 70vh; overflow-y: auto; background: #0c0f17; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: inset 0 0 20px rgba(0,255,204,0.05); }
        .msg { margin: 8px 0; border-bottom: 1px dashed #1b2330; padding-bottom: 5px; }
        input { background: #030407; border: 1px solid #ff3333; color: #00ffcc; padding: 12px; width: 70%; font-family: monospace; }
        button { background: #ff3333; color: #fff; border: none; padding: 12px 20px; cursor: pointer; font-family: monospace; font-weight: bold; }
    </style></head><body>
    <h2 style="color:#ff3333; border-bottom:2px solid #ff3333; padding-bottom:8px;">■ SCP FOUNDATION INTRANET TERMINAL</h2>
    <div id="log"></div>
    <input type="text" id="user" placeholder="OPERATOR ID" style="width:15%; margin-right:10px;">
    <input type="text" id="msg" placeholder="Type tactical message data packets... (Press Enter)">
    <button onclick="send()">TRANSMIT</button>
    <script>
        let myUser = "ANONYMOUS";
        async function fetchLog() {
            try {
                let res = await fetch('/api/history'); let data = await res.json();
                let log = document.getElementById("log"); log.innerHTML = "";
                data.forEach(m => { log.innerHTML += `<div class="msg"><span style="color:#ff3333">[${m.time}]</span> <span style="color:#00ffcc">${m.user}:</span> ${m.text}</div>`; });
            } catch(e){}
        }
        async function send() {
            let uInput = document.getElementById("user").value.trim(); if(uInput) myUser = uInput.toUpperCase();
            let mInput = document.getElementById("msg"); let text = mInput.value.trim(); if(!text) return; mInput.value = "";
            await fetch('/api/transmit', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ user: myUser, text: text }) });
            fetchLog();
        }
        document.getElementById("msg").addEventListener("keypress", (e) => { if(e.key === "Enter") send(); });
        fetchLog(); setInterval(fetchLog, 1500);
    </script></body></html>
    """
    return HTMLResponse(content=html_layout, status_code=200)

@app.get("/api/history")
async def get_history():
    return messages_db

@app.post("/api/transmit")
async def transmit_message(payload: MessageModel):
    now = datetime.now().strftime("%H:%M:%S")
    messages_db.append({"user": payload.user, "text": payload.text, "time": now})
    return {"status": "TRANSMITTED"}
