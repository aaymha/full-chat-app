import asyncio
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
            except(KeyboardInterrupt, ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
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
        await websocket.drain()


async def user_connected(id_user, nickname, websocket):
    await websocket.send(f"{nickname} joined the chat, ID: {id_user}")
    connected_users[id_user] = websocket
    await websocket.drain()


async def user_disconnected(id_user, nickname, websocket):
    if id_user in connected_users:
        del connected_users[id_user]
        await broadcast(f"{nickname} left the chat", websocket)

async def main():
    async with serve(client_one, '0.0.0.0', 8888) as server:
        await server.serve_forever()

asyncio.run(main())