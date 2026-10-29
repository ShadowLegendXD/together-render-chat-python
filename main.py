import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="SCP Foundation Tactical Hub")

messages_db = [
    {"user": "SYSTEM", "text": "[SECURE. CONTAIN. PROTECT.] Network operational.", "time": "00:00:00"}
]

class MessageModel(BaseModel):
    user: str
    text: str

@app.get("/", response_class=HTMLResponse)
async def get_terminal():
    html_layout = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SCP Foundation - Site Control Lounge</title>
        <style>
            :root {
                --bg-main: #07090e; --panel-bg: #0c0f17; --scp-crimson: #ff3333;
                --terminal-cyan: #00ffcc; --border-color: #1b2330; --text-muted: #6272a4;
            }
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: var(--bg-main); color: #f8f8f2; font-family: 'Courier New', Courier, monospace; overflow: hidden; }
            #login-overlay { position: fixed; top:0; left:0; width:100%; height:100%; background: var(--bg-main); z-index: 1000; display: flex; flex-direction: column; justify-content: center; align-items: center; border: 4px solid var(--scp-crimson); box-sizing: border-box; }
            .login-box { background: var(--panel-bg); padding: 30px; border: 1px solid var(--border-color); border-radius: 4px; text-align: center; max-width: 400px; box-shadow: 0 0 20px rgba(255, 51, 51, 0.1); }
            .login-input { background: #030407; border: 1px solid var(--scp-crimson); color: var(--terminal-cyan); padding: 12px; font-family: monospace; width: 80%; font-size: 16px; margin: 15px 0; text-align: center; }
            .login-btn { background: var(--scp-crimson); color: white; border: none; padding: 10px 25px; cursor: pointer; font-weight: bold; font-family: monospace; letter-spacing: 2px; }
            .app-container { display: flex; width: 100vw; height: 100vh; }
            .sidebar { width: 320px; background: var(--panel-bg); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; }
            .scp-brand { font-size: 18px; color: var(--scp-crimson); border-bottom: 2px solid var(--scp-crimson); padding-bottom: 10px; margin-bottom: 20px; text-shadow: 0 0 5px rgba(255, 51, 51, 0.3); }
            .ac-control-panel { background: #040508; border: 1px solid var(--border-color); padding: 12px; border-radius: 4px; margin-bottom: 20px; }
            .ac-unit { display: flex; justify-content: space-between; align-items: center; margin: 8px 0; font-size: 12px; }
            .status-indicator { width: 8px; height: 8px; border-radius: 5px; display: inline-block; background: var(--terminal-cyan); box-shadow: 0 0 8px var(--terminal-cyan); }
            .ac-animation { animation: pulse 2s infinite ease-in-out; }
            @keyframes pulse { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }
            .chat-area { flex: 1; display: flex; flex-direction: column; background: #05060a; }
            .chat-header { background: var(--panel-bg); padding: 15px 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
            .chat-history { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; box-shadow: inset 0 0 30px rgba(0,0,0,0.5); }
            .msg-wrapper { display: flex; width: 100%; margin: 2px 0; }
            .msg-wrapper.outgoing { justify-content: flex-end; }
            .msg-wrapper.incoming { justify-content: flex-start; }
            .bubble { max-width: 65%; padding: 10px 14px; border-radius: 6px; font-size: 14px; line-height: 1.4; position: relative; }
            .msg-wrapper.outgoing .bubble { background: #161f2e; border: 1px solid var(--terminal-cyan); border-top-right-radius: 0; color: #fff; }
            .msg-wrapper.incoming .bubble { background: #12141c; border: 1px solid var(--border-color); border-top-left-radius: 0; }
            .bubble-meta { font-size: 10px; color: var(--text-muted); display: block; text-align: right; margin-top: 4px; font-family: sans-serif; }
            .operator-tag { font-size: 11px; font-weight: bold; color: var(--scp-crimson); display: block; margin-bottom: 3px; }
            .input-container { background: var(--panel-bg); padding: 15px 20px; border-top: 1px solid var(--border-color); display: flex; gap: 15px; align-items: center; }
            .message-input { flex: 1; background: #030407; border: 1px solid var(--border-color); color: #fff; padding: 14px; border-radius: 4px; font-family: monospace; font-size: 14px; outline: none; }
            .message-input:focus { border-color: var(--terminal-cyan); }
            .send-btn { background: #1a2332; border: 1px solid var(--terminal-cyan); color: var(--terminal-cyan); padding: 12px 28px; cursor: pointer; border-radius: 4px; font-weight: bold; font-family: monospace; transition: 0.2s; }
            .send-btn:hover { background: var(--terminal-cyan); color: #000; box-shadow: 0 0 10px var(--terminal-cyan); }
        </style>
    </head>
    <body>
        <div id="login-overlay">
            <div class="login-box">
                <div style="color: var(--scp-crimson); font-weight: bold; margin-bottom: 5px;">[WARNING]</div>
                <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 15px;">RESTRICTED INTRANET NETWORK LINKED</div>
                <input type="text" id="credential-input" class="login-input" placeholder="OPERATOR ID (e.g. O5-SHADOW)" autofocus>
                <br>
                <button onclick="authorizeOperator()" class="login-btn">INITIALIZE CLEARANCE</button>
            </div>
        </div>
        <div class="app-container">
            <div class="sidebar">
                <div class="scp-brand">■ SCP FOUNDATION <span style="font-size:10px; color:var(--text-muted);">v3.14</span></div>
                <div style="font-size: 11px; color: var(--scp-crimson); font-weight: bold; margin-bottom: 6px;">[HVAC AMBIENT SYSTEMS]</div>
                <div class="ac-control-panel">
                    <div class="ac-unit"><span>AC-01 (MAIN CORE)</span><div><span style="color: var(--terminal-cyan);">16°C</span> <span class="status-indicator ac-animation"></span></div></div>
                    <div class="ac-unit"><span>AC-02 (CONTAINMENT)</span><div><span style="color: var(--terminal-cyan);">14°C</span> <span class="status-indicator ac-animation"></span></div></div>
                </div>
                <div style="margin-top:auto; font-size:10px; color: var(--text-muted); line-height: 1.4; border-top: 1px solid var(--border-color); padding-top: 10px;">
                    DATA PARSING: CLOUD ACTIVE<br>PC DISK STORAGE: <span style="color:var(--terminal-cyan);">0.00 MB USED</span>
                </div>
            </div>
            <div class="chat-area">
                <div class="chat-header">
                    <div><span style="color: var(--scp-crimson); font-weight: bold;">[SECURE LOUNGE]</span><span style="font-size:11px; color:var(--text-muted); margin-left:10px;">End-to-End Encryption Buffer</span></div>
                    <div style="font-size:12px; color:var(--terminal-cyan);" id="operator-display">OP: UNKNOWN</div>
                </div>
                <div class="chat-history" id="chat-frame"></div>
                <div class="input-container">
                    <input type="text" id="msg-input" class="message-input" placeholder="Type tactical message data packets..." disabled>
                    <button id="send-trigger" class="send-btn" onclick="transmitMessage()" disabled>TRANSMIT</button>
                </div>
            </div>
        </div>
        <script>
            let currentOperator = "";
            function authorizeOperator() {
                const name = document.getElementById("credential-input").value.trim();
                if(!name) return;
                currentOperator = name.toUpperCase();
                document.getElementById("login-overlay").style.display = "none";
                document.getElementById("operator-display").innerText = "OP: " + currentOperator;
                document.getElementById("msg-input").disabled = false;
                document.getElementById("send-trigger").disabled = false;
                document.getElementById("msg-input").focus();
                fetchHistory(); setInterval(fetchHistory, 1500);
            }
            async function fetchHistory() {
                try {
                    const response = await fetch('/api/history');
                    const messages = await response.json();
                    const frame = document.getElementById("chat-frame");
                    const shouldScroll = frame.scrollTop + frame.clientHeight >= frame.scrollHeight - 50;
                    frame.innerHTML = "";
                    messages.forEach(msg => {
                        const isMe = msg.user === currentOperator;
                        const wrapper = document.createElement("div");
                        wrapper.className = `msg-wrapper ${isMe ? 'outgoing' : 'incoming'}`;
                        wrapper.innerHTML = `<div class="bubble">${!isMe ? `<span class="operator-tag">${msg.user}</span>` : ''}<div>${msg.text}</div><span class="bubble-meta">${msg.time}</span></div>`;
                        frame.appendChild(wrapper);
                    });
                    if(shouldScroll) frame.scrollTop = frame.scrollHeight;
                } catch (e) { console.error(e); }
            }
            async function transmitMessage() {
                const input = document.getElementById("msg-input");
                const text = input.value.trim(); if(!text) return; input.value = "";
                await fetch('/api/transmit', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ user: currentOperator, text: text }) });
                fetchHistory();
            }
            document.getElementById("msg-input").addEventListener("keypress", (e) => { if(e.key === "Enter") transmitMessage(); });
        </script>
    </body>
    </html>
    \"\"\"
    return HTMLResponse(content=html_layout, status_code=200)

@app.get("/api/history")
async def get_history():
    return messages_db

@app.post("/api/transmit")
async def transmit_message(payload: MessageModel):
    now = datetime.now().strftime("%H:%M:%S")
    messages_db.append({"user": payload.user, "text": payload.text, "time": now})
    return {"status": "TRANSMITTED"}
