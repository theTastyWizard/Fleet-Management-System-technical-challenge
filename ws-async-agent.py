import uuid
import asyncio
import aiohttp
import websockets
import json

SERVER_URL = "http://127.0.0.1:8000"
SERVER_WS = "ws://127.0.0.1:8000"
AGENT_ID = str(uuid.uuid4())
AGENT_NAME = "WebSocketAsyncTest1"


async def register(session):
    async with session.post(
        f"{SERVER_URL}/agents/register", json={"id": AGENT_ID, "name": AGENT_NAME}
    ) as r:
        print("Agent registered:", r.json())


async def execute_cmd(command):
    print(f"Executing command: {command}")
    # simulation of execution
    await asyncio.sleep(2)
    results = f"Executed '{command}' successfully."
    return results


async def send_result(session, cmd_id, result):
    async with session.post(
        f"{SERVER_URL}/responses/{AGENT_ID}/{cmd_id}", params={"result": result}
    ) as r:
        print("Sent result:", await r.json())


async def listen_for_commands():
    async with aiohttp.ClientSession() as session:
        await register(session)
        while True:
            try:
                async with websockets.connect(f"{SERVER_WS}/ws/{AGENT_ID}") as ws:
                    print(f"[{AGENT_NAME}] connected to websocket")
                    # deal with messages/commands
                    async for message in ws:
                        data = json.loads(message)
                        cmd_id = data["id"]
                        cmd = data["command"]
                        result = await execute_cmd(cmd)
                        await send_result(session, cmd_id, result)
            except (websockets.ConnectionClosed, ConnectionError):
                print(f"[{AGENT_NAME}] connection lost. Retrying in 5s")
                await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(listen_for_commands())
