from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import os
import uvicorn
from database import init_database, save_message, recent_messages

app = FastAPI()
connected_users = {}
user_names = {}

@app.get("/")
@app.head("/")
async def load_site():
    return FileResponse("site.html")

@app.get("/{filename}")
@app.head("/{filename}")
async def load_backend(filename: str):
    if filename in ["script.js", "style.css"]:
        return FileResponse(filename)
    return {"error": "File not found"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    init_database()
    await websocket.accept()

    user_id = id(websocket)

    try:
        username = await websocket.receive_text()
        username.strip()

        connected_users[user_id] = websocket
        user_names[user_id] = username
        message_when_user_joins = f"{username} joined the chat! Welcome him :)"

        stored_message = "\n".join(recent_messages())
        await websocket.send_text(stored_message)
        
        for users in connected_users.values():
            await users.send_text(message_when_user_joins)

        while True:
            user_message = await websocket.receive_text()
            save_message(username, user_message)
            print(f"{username} + {user_message}")

            for user_ws in connected_users.values():
                try:
                    await user_ws.send_text(user_message)
                except ValueError:
                    pass

    except WebSocketDisconnect:
        if user_id in connected_users and user_id in user_names:
            del connected_users[user_id]
            username = user_names[user_id]
            del user_names[user_id]

            message_when_user_leaves = f"{username} left the chat, goodbye"

            for user_ws in connected_users.values():
                try:
                    await user_ws.send_text(message_when_user_leaves)
                except ValueError:
                    pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)