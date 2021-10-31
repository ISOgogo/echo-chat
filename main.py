from fastapi import FastAPI, WebSocket, Form, Request, Header
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Optional
from login import UserCreateForm
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates/")

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.client_ids = []

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.connections.append(websocket)
        self.client_ids.append(client_id)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)
    
    def disconnect(self, websocket: WebSocket):

        for index, ws in enumerate(self.connections):
            if ws == websocket:
                self.connections.pop(index)
                self.client_ids.pop(index)

manager = ConnectionManager()
    
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    await manager.broadcast(f"User {client_id} joined the chat")

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{client_id}: {data}")
            rand_user = random.choice(manager.client_ids)
            await manager.broadcast(f"{rand_user}: {data}")
    except:
        manager.disconnect(websocket)
        await manager.broadcast(f"User {client_id} left the chat")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
async def index(request: Request):
    form = UserCreateForm(request)
    await form.load_data()
    if await form.is_valid() == False:
        return templates.TemplateResponse("index.html", form.__dict__)
    return templates.TemplateResponse("chat.html", form.__dict__)
