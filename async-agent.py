import uuid
import asyncio
import aiohttp

SERVER_URL = "http://127.0.0.1:8000"
AGENT_ID = str(uuid.uuid4())
AGENT_NAME = "AsyncTest1"


async def register(session):
    async with session.post(
        f"{SERVER_URL}/agents/register", json={"id": AGENT_ID, "name": AGENT_NAME}
    ) as r:
        print("Agent registered:", r.json())


async def execute_cmd(command):
    print(f"Executing command: {command}")
    results = f"Executed '{command}' successfully."
    return results


async def send_result(session, cmd_id, result):
    async with session.post(
        f"{SERVER_URL}/responses/{AGENT_ID}/{cmd_id}", params={"result": result}
    ) as r:
        print("Sent result:", await r.json())


async def poll(session):
    while True:
        async with session.get(f"{SERVER_URL}/commands/{AGENT_ID}") as r:
            data = await r.json()
            if "command" in data:
                cmd = data["command"]
                cmd_id = data["id"]
                # simulation of execution
                await asyncio.sleep(2)
                result = await execute_cmd(cmd)
                await send_result(session, cmd_id, result)
            else:
                print("No commands. Sleeping")
                await asyncio.sleep(5)


async def main():
    async with aiohttp.ClientSession() as session:
        await register(session)
        await poll(session)


if __name__ == "__main__":
    asyncio.run(main())
