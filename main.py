import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

app = FastAPI(title="SCP Foundation Tactical Grid")

# Cloud Memory Banks (Zero Disk Footprint)
users_db: Dict[str, str] = {}  # username: password
contacts_db: Dict[str, List[str]] = {}  # username: list of contact names
groups_db: Dict[str, Dict] = {}  # group_name: {"creator": str, "members": List[str], "messages": List[Dict]}
private_messages: Dict[str, List[Dict]] = {}  # combo_string: list of messages

class AuthModel(BaseModel):
    username: str
    password: str

class ContactModel(BaseModel):
    username: str
    target: str

class GroupCreateModel(BaseModel):
    group_name: str
    creator: str
    members: List[str]

class MessageModel(BaseModel):
    sender: str
    target: str
    text: str
    is_group: bool

@app.get("/", response_class=HTMLResponse)
async def get_hub():
    if os.path.exists("public/index.html"):
        with open("public/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    return HTMLResponse(content="<h2>Error: public/index.html missing. Check file path framework.</h2>", status_code=404)

@app.post("/api/register")
async def register(data: AuthModel):
    user = data.username.upper().strip()
    if user in users_db:
        return {"status": "EXISTS"}
    users_db[user] = data.password
    contacts_db[user] = []
    return {"status": "SUCCESS"}

@app.post("/api/login")
async def login(data: AuthModel):
    user = data.username.upper().strip()
    if user in users_db and users_db[user] == data.password:
        return {"status": "SUCCESS"}
    return {"status": "FAILED"}

@app.get("/api/users")
async def get_all_users():
    return list(users_db.keys())

@app.post("/api/contacts/add")
async def add_contact(data: ContactModel):
    user = data.username.upper()
    target = data.target.upper()
    if target in users_db and target not in contacts_db[user]:
        contacts_db[user].append(target)
        return {"status": "ADDED"}
    return {"status": "FAILED"}

@app.get("/api/contacts/{username}")
async def get_contacts(username: str):
    return contacts_db.get(username.upper(), [])

@app.post("/api/groups/create")
async def create_group(data: GroupCreateModel):
    g_name = data.group_name.upper().strip()
    if g_name in groups_db:
        return {"status": "EXISTS"}
    members = [m.upper() for m in data.members]
    members.append(data.creator.upper())
    groups_db[g_name] = {"creator": data.creator.upper(), "members": list(set(members)), "messages": []}
    return {"status": "SUCCESS"}

@app.get("/api/groups/{username}")
async def get_user_groups(username: str):
    user = username.upper()
    accessible_groups = []
    for g_name, g_info in groups_db.items():
        if user in g_info["members"]:
            accessible_groups.append(g_name)
    return accessible_groups

@app.post("/api/messages/transmit")
async def transmit(data: MessageModel):
    now = datetime.now().strftime("%H:%M")
    msg_packet = {"sender": data.sender.upper(), "text": data.text, "time": now}
    
    if data.is_group:
        g_name = data.target.upper()
        if g_name in groups_db:
            groups_db[g_name]["messages"].append(msg_packet)
            return {"status": "TRANSMITTED"}
    else:
        # Private Message Room Key Sort
        key = "-".join(sorted([data.sender.upper(), data.target.upper()]))
        if key not in private_messages:
            private_messages[key] = []
        private_messages[key].append(msg_packet)
        return {"status": "TRANSMITTED"}
    return {"status": "FAILED"}

@app.get("/api/messages/fetch")
async def fetch_messages(sender: str, target: str, is_group: bool):
    if is_group:
        g_name = target.upper()
        if g_name in groups_db:
            return groups_db[g_name]["messages"]
    else:
        key = "-".join(sorted([sender.upper(), target.upper()]))
        return private_messages.get(key, [])
    return []
