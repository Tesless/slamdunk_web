from pymongo import MongoClient

client = MongoClient("mongodb+srv://tesless:123@cluster0.xyeyaz7.mongodb.net/test")
db = client["test"]
collection = db["dw"]

from fastapi import FastAPI, WebSocket,  Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: str):
        for connection in self.active_connections:
            await connection.send_text(data)

manager = ConnectionManager()

@app.get('/',response_class=HTMLResponse) 
async def read_item(request: Request):  
	return templates.TemplateResponse("index.html", {"request": request}) 

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard2.html",{"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = collection.find_one()
            await manager.broadcast(data)
            print(type(data))
    except:
        manager.disconnect(websocket)
    