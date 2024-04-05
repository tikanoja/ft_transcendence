# import asyncio
# import websockets

# async def hello():
#     async with websockets.connect("wss://localhost:8765") as websocket:
#         await websocket.send("Hello, server!")
#         response = await websocket.recv()
#         print(f"Received from server: {response}")

# asyncio.run(hello())

import asyncio
import ssl
import websockets

async def hello():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # Ignore certificate verification

    async with websockets.connect("wss://localhost:8888", ssl=ssl_context) as websocket:
        await websocket.send("Hello, server!")
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.run(hello())
