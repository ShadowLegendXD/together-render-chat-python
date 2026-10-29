import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="SCP Foundation Tactical Hub")

messages_db = [
    {"user": "SYSTEM", "text": "[O5-LEVEL CLEARANCE GRANTED] Intranet link live.", "time": "00:00"}
]

class MessageModel(BaseModel):
    user: str
    text: str

@app.get("/", response_class=HTMLResponse)
async def get_terminal():
    premium_ui = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>SCP Intranet Console</title>
        <style>
            :root {
                --bg-main: #05070a; --panel-bg: #0b0e14; --scp-red: #ff3333;
                --neon-cyan: #00ffcc; --border: #141b26; --bubble-out: #162435; --bubble-in: #0f1218;
            }
            body, html { margin:0; padding:0; width:100%; height:100%; background:var(--bg-main); color:#f8f8f2; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; overflow:hidden; }
            #auth-gate { position:fixed; top:0; left:0; width:100%; height:100%; background:var(--bg-main); z-index:9999; display:flex; justify-content:center; align-items:center; border:3px solid var(--scp-red); box-sizing:border-box; }
            .gate-card { background:var(--panel-bg); border:1px solid var(--border); padding:30px; border-radius:12px; text-align:center; max-width:340px; width:88%; box-shadow:0 0 30px rgba(255,51,51,0.15); }
            .gate-input { background:#020305; border:1px solid var(--scp-red); color:var(--neon-cyan); padding:12px; font-family:monospace; width:85%; font-size:15px; border-radius:6px; margin:15px 0; text-align:center; outline:none; }
            .gate-btn { background:var(--scp-red); color:#fff; border:none; padding:12px; font-size:13px; font-weight:bold; letter-spacing:2px; border-radius:6px; cursor:pointer; font-family:monospace; width:100%; }
            .workspace { display:flex; width:100vw; height:100vh; background:#020305; }
            .sidebar { width:300px; background:var(--panel-bg); border-right:1px solid var(--border); display:flex; flex-direction:column; box-sizing:border-box; }
            .brand-header { padding:15px; font-size:14px; font-family:monospace; font-weight:bold; color:var(--scp-red); border-bottom:1px solid var(--border); display:flex; align-items:center; gap:10px; }
            .hvac-widget { padding:15px; background:#030406; border-bottom:1px solid var(--border); }
            .ac-row { display:flex; justify-content:space-between; align-items:center; margin:8px 0; font-family:monospace; font-size:11px; }
            .glow-dot { width:7px; height:7px; border-radius:50%; background:var(--neon-cyan); box-shadow:0 0 8px var(--neon-cyan); animation:blink 2s infinite; }
            @keyframes blink { 0%,100%{opacity:.4} 50%{opacity:1} }
            .chat-lounge { flex:1; display:flex; flex-direction:column; background:#040608; height:100%; position:relative; }
            .chat-topbar { background:var(--panel-bg); padding:15px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; box-sizing:border-box; }
            .chat-feed { flex:1; padding:15px; overflow-y:auto; display:flex; flex-direction:column; gap:8px; box-sizing:border-box; margin-bottom:70px; }
            .row-pack { display:flex; width:100%; margin:1px 0; }
            .row-pack.me { justify-content:flex-end; }
            .row-pack.them { justify-content:flex-start; }
            .bubble { max-width:75%; padding:10px 12px; border-radius:8px; font-size:14px; line-height:1.4; box-shadow:0 1px 2px rgba(0,0,0,0.2); position:relative; animation:slideUpGlow 0.4s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; opacity:0; transform:translateY(10px); }
            @keyframes slideUpGlow { to { opacity:1; transform:translateY(0); } }
            .row-pack.me .bubble { background:var(--bubble-out); border:1px solid rgba(0,255,204,0.15); border-top-right-radius:0; color:#fff; }
            .row-pack.them .bubble { background:var(--bubble-in); border:1px solid var(--border); border-top-left-radius:0; }
            .bubble-time { font-size:9px; color:#526284; display:block; text-align:right; margin-top:4px; font-family:sans-serif; }
            .user-tag { font-size:11px; font-weight:bold; color:var(--scp-red); font-family:monospace; display:block; margin-bottom:3px; }
            .bottom-bar { position:absolute; bottom:0; left:0; width:100%; background:var(--panel-bg); padding:12px 15px; border-top:1px solid var(--border); display:flex; gap:10px; align-items:center; box-sizing:border-box; z-index:10; }
            .text-input { flex:1; background:#020305; border:1px solid var(--border); color:#fff; padding:12px; border-radius:8px; font-size:14px; outline:none; -webkit-appearance:none; }
            .text-input:focus { border-color:var(--neon-cyan); }
            .send-btn { background:#121a24; border:1px solid var(--neon-cyan); color:var(--neon-cyan); padding:12px 20px; font-size:12px; font-weight:bold; cursor:pointer; border-radius:8px; font-family:monospace; }
            @media (max-width: 768px) {
                .sidebar { display:none; }
                .bubble { max-width:85%; }
            }
        </style>
    </head>
    <body>
        <div id="auth-gate">
            <div class="gate-card">
                <svg width="60" height="60" viewBox="0 0 100 100" style="margin-bottom:10px;">
                    <circle cx="50" cy="50" r="40" stroke="#ff3333" stroke-width="3" fill="none" />
                    <circle cx="50" cy="50" r="28" stroke="#ff3333" stroke-width="1.5" fill="none" stroke-dasharray="4 2" />
                    <line x1="50" y1="10" x2="50" y2="35" stroke="#ff3333" stroke-width="4" />
                    <polygon points="50,38 46,32 54,32" fill="#ff3333" />
                    <line x1="15" y1="70" x2="36" y2="58" stroke="#ff3333" stroke-width="4" />
                    <polygon points="38,57 32,54 36,61" fill="#ff3333" />
                    <line x1="85" y1="70" x2="64" y2="58" stroke="#ff3333" stroke-width="4" />
                    <polygon points="62,57 64,61 68,54" fill="#ff3333" />
                </svg>
                <div style="color:var(--scp-red); font-weight:bold; font-family:monospace; font-size:16px;">■ O5 CLEARANCE ACCESS</div>
                <input type="text" id="gate-username" class="gate-input" placeholder="OPERATOR IDENTIFIER" autofocus>
                <button onclick="registerLoungeSession()" class="gate-btn">INITIALIZE CORE FEED</button>
            </div>
        </div>
        <div class="workspace">
            <div class="sidebar">
                <div class="brand-header">
                    <svg width="20" height="20" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" stroke="#ff3333" stroke-width="6" fill="none"/><line x1="50" y1="10" x2="50" y2="35" stroke="#ff3333" stroke-width="8"/></svg>
                    <span>FOUNDATION CORE v5.0</span>
                </div>
                <div class="hvac-widget">
                    <div style="font-size:10px; font-weight:bold; color:var(--scp-red); margin-bottom:6px;">[SITE WING SYSTEMS]</div>
                    <div class="ac-row"><span>CORE AC-01</span><div><span style="color:var(--neon-cyan); font-weight:bold; margin-right:5px;">16°C</span><span class="glow-dot"></span></div></div>
                    <div class="ac-row"><span>CONTAIN AC-02</span><div><span style="color:var(--neon-cyan); font-weight:bold; margin-right:5px;">14°C</span><span class="glow-dot"></span></div></div>
                </div>
                <div style="margin-top:auto; padding:15px; font-family:monospace; font-size:10px; color:#526284; border-top:1px solid var(--border);">DISK FOOTPRINT: 0.00 MB</div>
            </div>
            <div class="chat-lounge">
                <div class="chat-topbar">
                    <div style="font-weight:bold; font-family:monospace; font-size:13px; color:var(--scp-red);">📡 [SECURE INTRANET HUB]</div>
                    <div style="font-size:12px; color:var(--neon-cyan); font-family:monospace;" id="handle-tag">OP: UNKNOWN</div>
                </div>
                <div class="chat-feed" id="chat-scroller"></div>
                <div class="bottom-bar">
                    <input type="text" id="chat-input" class="text-input" placeholder="Type encrypted data packet..." disabled>
                    <button id="chat-trigger" class="send-btn" onclick="firePacket()" disabled>TRANSMIT</button>
                </div>
            </div>
        </div>
        <script>
            let operatorHandle = "";
            let audioCtx = null;
            function playO5Drone() {
                try {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    let osc1 = audioCtx.createOscillator(); let osc2 = audioCtx.createOscillator(); let gainNode = audioCtx.createGain();
                    osc1.type = "sawtooth"; osc1.frequency.setValueAtTime(55, audioCtx.currentTime); 
                    osc2.type = "sine"; osc2.frequency.setValueAtTime(55.5, audioCtx.currentTime);
                    let filter = audioCtx.createBiquadFilter(); filter.type = "lowpass"; filter.frequency.setValueAtTime(120, audioCtx.currentTime);
                    gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);
                    osc1.connect(filter); osc2.connect(filter); filter.connect(gainNode); gainNode.connect(audioCtx.destination);
                    osc1.start(); osc2.start();
                } catch(e){}
            }
            function registerLoungeSession() {
                let val = document.getElementById("gate-username").value.trim(); if(!val) return;
                operatorHandle = val.toUpperCase();
                document.getElementById("auth-gate").style.display = "none";
                document.getElementById("handle-tag").innerText = "OP: " + operatorHandle;
                document.getElementById("chat-input").disabled = false;
                document.getElementById("chat-trigger").disabled = false;
                document.getElementById("chat-input").focus();
                playO5Drone(); syncTerminalStream(); setInterval(syncTerminalStream, 1400);
            }
            async function syncTerminalStream() {
                try {
                    let res = await fetch('/api/history'); let messages = await res.json();
                    let pane = document.getElementById("chat-scroller");
                    let autoScroll = pane.scrollTop + pane.clientHeight >= pane.scrollHeight - 100;
                    pane.innerHTML = "";
                    messages.forEach(m => {
                        let isMe = m.user === operatorHandle;
                        let block = document.createElement("div"); block.className = `row-pack ${isMe ? 'me' : 'them'}`;
                        block.innerHTML = `<div class="bubble">${!isMe ? `<span class="user-tag">${m.user}</span>`:'' }<div>${m.text}</div><span class="bubble-time">${m.time}</span></div>`;
                        pane.appendChild(block);
                    });
                    if(autoScroll) pane.scrollTop = pane.scrollHeight;
                } catch(e){}
            }
            async function firePacket() {
                let field = document.getElementById("chat-input"); let val = field.value.trim(); if(!val) return; field.value = "";
                await fetch('/api/transmit', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ user:operatorHandle, text:val }) });
                syncTerminalStream();
            }
            document.getElementById("chat-input").addEventListener("keypress", (e) => { if(e.key === "Enter") firePacket(); });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=premium_ui, status_code=200)

@app.get("/api/history")
async def get_history():
    return messages_db

@app.post("/api/transmit")
async def transmit_message(payload: MessageModel):
    now = datetime.now().strftime("%H:%M")
    messages_db.append({"user": payload.user, "text": payload.text, "time": now})
    return {"status": "TRANSMITTED"}
