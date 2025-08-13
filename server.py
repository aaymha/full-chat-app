from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

app = FastAPI()


# Serve static files
@app.get("/")
@app.head("/")  # Allow HEAD requests for health checks
async def read_index():
    return FileResponse('chat.html')


@app.get("/{filename}")
@app.head("/{filename}")  # Allow HEAD requests
async def read_file(filename: str):
    if filename in ["script.js", "style.css"]:
        return FileResponse(filename)
    return {"error": "File not found"}


# WebSocket connection
connected_users = {}
user_names = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_id = id(websocket)

    try:
        # Get nickname
        nickname = await websocket.receive_text()
        nick = nickname.strip()

        # Add user
        connected_users[user_id] = websocket
        user_names[user_id] = nick

        # Announce user joined
        join_message = f"{nick} joined the chat, ID: {user_id}"
        await websocket.send_text(join_message)

        # Main message loop
        while True:
            message = await websocket.receive_text()
            print(f"{message}")

            # Broadcast to all connected users
            for ws in connected_users.values():
                try:
                    await ws.send_text(message)
                except:
                    pass

    except WebSocketDisconnect:
        pass
    finally:
        # Clean up when user disconnects
        if user_id in connected_users:
            del connected_users[user_id]
            if user_id in user_names:
                nick = user_names[user_id]
                del user_names[user_id]

                # Announce user left
                leave_message = f"{nick} left the chat"
                for ws in list(connected_users.values()):
                    try:
                        await ws.send_text(leave_message)
                    except:
                        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)