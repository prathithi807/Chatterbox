import asyncio
import websockets
import json

TOKEN ="beb206f1-5bf1-44fa-9d0a-991110cfbeee"
URI = f"ws://127.0.0.1:8000/ws?token={TOKEN}"


async def send_messages(websocket):
    loop = asyncio.get_event_loop()
    while True:
        text = await loop.run_in_executor(None, input, "> ")

        payload = {
            "content": text
        }

        await websocket.send(json.dumps(payload))


async def receive_messages(websocket):
    while True:
        raw = await websocket.recv()
        data = json.loads(raw)

        msg_type = data.get("type")

        if msg_type == "history":
            print("\n--- Chat History ---")
            for msg in data["messages"]:
                print(f"[{msg['timestamp']}] {msg['username']}: {msg['content']}")
            print("--------------------\n")

        elif msg_type == "message":
            print(f"[{data['timestamp']}] {data['username']}: {data['content']}")

        elif msg_type == "error":
            print(f"[Error] {data['detail']}")

        else:
            print("[Unknown message]", data)


async def chat():
    async with websockets.connect(URI) as websocket:
        print("Connected to chat server")

        await asyncio.gather(
            send_messages(websocket),
            receive_messages(websocket),
        )


if __name__ == "__main__":
    asyncio.run(chat())
