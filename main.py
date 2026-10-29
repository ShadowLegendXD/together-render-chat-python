import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="SCP Foundation Tactical Hub")

# Persistent Cloud Message Buffer
messages_db = [
    {"user": "SYSTEM", "text": "[SECURE. CONTAIN. PROTECT.] Intranet channel streaming active.", "time": "00:00:00"}
]

class MessageModel(BaseModel):
    user: str
    text: str

@app.get("/", response_class=HTMLResponse)
async def get_terminal():
    # Injecting the complete premium layout straight into the root memory frame to bypass folder overrides!
    premium_ui = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SCP Intranet Lounge</title>
        <style>
            :root {
                --bg-main: #06080c; --panel-bg: #0b0e14; --scp-red: #ff3333;
                --neon-cyan: #00ffcc; --border: #161e29; --bubble-out: #182535; --bubble-in: #11141b;
            }
            body, html { margin:0; padding:0; width:100%; height:100%; background:var(--bg-main); color:#f8f8f2; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; overflow:hidden; }
            #auth-gate { position:fixed; top:0; left:0; width:100%; height:100%; background:var(--bg-main); z-index:9999; display:flex; justify-content:center; align-items:center; border:4px solid var(--scp-red); box-sizing:border-box; }
            .gate-card { background:var(--panel-bg); border:1px solid var(--border); padding:35px; border-radius:12px; text-align:center; max-width:360px; width:90%; box-shadow:0 0 30px rgba(255,51,51,0.15); }
            .gate-input { background:#030406; border:1px solid var(--scp-red); color:var(--neon-cyan); padding:14px; font-family:monospace; width:85%; font-size:16px; border-radius:6px; margin:20px 0; text-align:center; outline:none; }
            .gate-btn { background:var(--scp-red); color:#fff; border:none; padding:12px 30px; font-size:14px; font-weight:bold; letter-spacing:2px; border-radius:6px; cursor:pointer; font-family:monospace; width:100%; }
            .workspace { display:flex; width:100vw; height:100vh; background:#040507; }
            .sidebar { width:320px; background:var(--panel-bg); border-right:1px solid var(--border); display:flex; flex-direction:column; box-sizing:border-box; }
            .brand-header { padding:20px; font-size:16px; font-family:monospace; font-weight:bold; color:var(--scp-red); border-bottom:1px solid var(--border); letter-spacing:1px; }
            .hvac-widget { padding:20px; background:#040507; border-bottom:1px solid var(--border); }
            .ac-row { display:flex; justify-content:space-between; align-items:center; margin:10px 0; font-family:monospace; font-size:12px; }
            .glow-dot { width:8px; height:8px; border-radius:50%; background:var(--neon-cyan); box-shadow:0 0 10px var(--neon-cyan); animation:blink 2s infinite; }
            @keyframes blink { 0%,100%{opacity:.4} 50%{opacity:1} }
            .chat-lounge { flex:1; display:flex; flex-direction:column; background:#05070a; }
            .chat-topbar { background:var(--panel-bg); padding:18px 25px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; }
            .chat-feed { flex:1; padding:25px; overflow-y:auto; display:flex; flex-direction:column; gap:8px; }
            .row-pack { display:flex; width:100%; margin:2px 0; }
            .row-pack.me { justify-content:flex-end; }
            .row-pack.them { justify-content:flex-start; }
            .bubble { max-width:65%; padding:10px 14px; border-radius:8px; font-size:14px; line-height:1.45; box-shadow:0 1px 2px rgba(0,0,0,0.3); position:relative; }
            .row-pack.me .bubble { background:var(--bubble-out); border:1px solid rgba(0,255,204,0.2); border-top-right-radius:0; color:#fff; }
            .row-pack.them .bubble { background:var(--bubble-in); border:1px solid var(--border); border-top-left-radius:0; }
            .bubble-time { font-size:10px; color:#6272a4; display:block; text-align:right; margin-top:5px; font-family:sans-serif; }
            .user-tag { font-size:11px; font-weight:bold; color:var(--scp-red); font-family:monospace; display:block; margin-bottom:4px; }
            .bottom-bar { background:var(--panel-bg); padding:15px 25px; border-top:1px solid var(--border); display:flex; gap:15px; align-items:center; }
            .text-input { flex:1; background:#030406; border:1px solid var(--border); color:#fff; padding:15px; border-radius:8px; font-size:14px; outline:none; }
            .send-btn { background:#151f2c; border:1px solid var(--neon-cyan); color:var(--neon-cyan); padding:14px 30px; font-size:13px; font-weight:bold; cursor:pointer; border-radius:8px; font-family:monospace; }
            .send-btn:hover { background:var(--neon-cyan); color:#000; box-shadow:0 0 15px var(--neon-cyan); }
        </style>
    </head>
    <body>
        <div id="auth-gate">
            <div class="gate-card">
                <div style="color:var(--scp-red); font-weight:bold; font-family:monospace; font-size:18px; margin-bottom:5px;">■ ACCREDITATION ENTRANCE</div>
                <input type="text" id="gate-username" class="gate-input" placeholder="CREATE HANDLE (e.g. O5-SHADOW)" autofocus>
                <button onclick="registerLoungeSession()" class="gate-btn">REGISTER ENTRY</button>
            </div>
        </div>
        <div class="workspace">
            <div class="sidebar">
                <div class="brand-header">📁 SCP INTRANET CORE v3.14</div>
                <div class="hvac-widget">
                    <div style="font-size:11px; font-weight:bold; color:var(--scp-red); margin-bottom:8px;">[HVAC AMBIENT SYSTEMS]</div>
                    <div class="ac-row"><span>AC-01 OPERATIONAL</span><div><span style="color:var(--neon-cyan); font-weight:bold; margin-right:6px;">16°C</span><span class="glow-dot"></span></div></div>
                    <div class="ac-row"><span>AC-02 OPERATIONAL</span><div><span style="color:var(--neon-cyan); font-weight:bold; margin-right:6px;">14°C</span><span class="glow-dot"></span></div></div>
                </div>
                <div style="margin-top:auto; padding:20px; font-family:monospace; font-size:11px; color:#6272a4; border-top:1px solid var(--border);">DISK SPACE USED: <span style="color:var(--neon-cyan);">0.00 MB</span></div>
            </div>
            <div class="chat-lounge">
                <div class="chat-topbar">
                    <div style="font-weight:bold; font-family:monospace; color:var(--scp-red);">[ACTIVE SECURE LOGS CHANNEL]</div>
                    <div style="font-size:13px; color:var(--neon-cyan); font-family:monospace; font-weight:bold;" id="handle-tag">OPERATOR: UNKNOWN</div>
                </div>
                <div class="chat-feed" id="chat-scroller"></div>
                <div class="bottom-bar">
                    <input type="text" id="chat-input" class="text-input" placeholder="Type secure message packets here..." disabled>
                    <button id="chat-trigger" class="send-btn" onclick="firePacket()" disabled>TRANSMIT</button>
                </div>
            </div>
        </div>
        <script>
            let operatorHandle = "";
            function registerLoungeSession() {
                let val = document.getElementById("gate-username").value.trim(); if(!val) return;
                operatorHandle = val.toUpperCase();
                document.getElementById("auth-gate").style.display = "none";
                document.getElementById("handle-tag").innerText = "OP: " + operatorHandle;
                document.getElementById("chat-input").disabled = false;
                document.getElementById("chat-trigger").disabled = false;
                document.getElementById("chat-input").focus();
                syncTerminalStream(); setInterval(syncTerminalStream, 1500);
            }
            async function syncTerminalStream() {
                try {
                    let res = await fetch('/api/history'); let messages = await res.json();
                    let pane = document.getElementById("chat-scroller");
                    let autoScroll = pane.scrollTop + pane.clientHeight >= pane.scrollHeight - 60;
                    pane.innerHTML = "";
                    messages.forEach(m => {
                        let isMe = m.user === operatorHandle;
                        let block = document.createElement("div");
                        block.className = `row-pack ${isMe ? 'me' : 'them'}`;
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
    now = datetime.now().strftime("%H:%M:%S")
    messages_db.append({"user": payload.user, "text": payload.text, "time": now})
