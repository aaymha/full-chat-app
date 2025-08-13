import asyncio
import os
import threading
import http.server
import socketserver
from os import write
import websockets
from websockets.asyncio.server import serve

connected_users = {}
user_names = {}


async def client_one(websocket):
    user_id = id(websocket)
    try:
        nickname = await websocket.recv()
        nick = nickname
        await user_connected(user_id, nick.strip(), websocket)
        await username(nick, user_id)
        name = user_names[user_id]

        while True:
            data = await websocket.recv()
            try:
                if not data:
                    await user_disconnected(user_id, nick.strip(), websocket)
                    break
            except(KeyboardInterrupt, ConnectionError, ConnectionAbortedError, ConnectionRefusedError,
                   ConnectionResetError):
                await user_disconnected(user_id, nick.strip(), websocket)
                break

            message = data
            print(f"{message.strip()}")
            await broadcast(message, websocket)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if user_id in connected_users:
            await user_disconnected(user_id, nick.strip(), websocket)

    await websocket.close()


async def username(nickname, id_user):
    user_names[id_user] = nickname
    print(user_names)


async def broadcast(namemess, sender):
    for websocket in connected_users.values():
        await websocket.send(namemess)


async def user_connected(id_user, nickname, websocket):
    await websocket.send(f"{nickname} joined the chat, ID: {id_user}")
    connected_users[id_user] = websocket


async def user_disconnected(id_user, nickname, websocket):
    if id_user in connected_users:
        del connected_users[id_user]
        await broadcast(f"{nickname} left the chat", websocket)


def start_http_server(port):

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()

    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"HTTP server serving at port {port}")
        httpd.serve_forever()


async def main():
    port = int(os.environ.get("PORT", 8888))

    print(f"Starting servers on port {port}")

    http_thread = threading.Thread(
        target=start_http_server,
        args=(port,),
        daemon=True
    )
    http_thread.start()

    async with serve(client_one, '0.0.0.0', port, path="/ws") as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())