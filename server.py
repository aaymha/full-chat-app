from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import os
import uvicorn
import sqlite3
from database import init_database, save_message, recent_messages

app = FastAPI()

@app.get("/")
@app.head("/")
async def read_index():
    return FileResponse('chat.html')


@app.get("/{filename}")
@app.head("/{filename}")
async def read_file(filename: str):
    if filename in ["script.js", "style.css"]:
        return FileResponse(filename)
    return {"error": "File not founds!"}


# WebSocket connection
connected_users = {}
user_names = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await init_database()
    await websocket.accept()
    user_id = id(websocket)

    try:
        nickname = await websocket.receive_text()
        nick = nickname.strip()

        connected_users[user_id] = websocket
        user_names[user_id] = nick

        join_message = f"{nick} joined the cha! ID: {user_id}"
        await websocket.send_text(join_message)
        message_string = '\n'.join(recent_messages())
        await websocket.send_text(message_string)


        while True:
            message = await websocket.receive_text()
            await save_message(nick, message)
            print(f"{nick} + {message}")

            for ws in connected_users.values():
                try:
                    await ws.send_text(message)
                except:
                    pass

    except WebSocketDisconnect:
        pass
    finally:
        if user_id in connected_users:
            del connected_users[user_id]
            if user_id in user_names:
                nick = user_names[user_id]
                del user_names[user_id]

                leave_message = f"{nick} left the chat"
                for ws in list(connected_users.values()):
                    try:
                        await ws.send_text(leave_message)
                    except:
                        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)