from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
import asyncio

app = FastAPI(title="Fleet Management API")


class Agent(BaseModel):
    id: str
    name: str


class Command(BaseModel):
    id: str
    command: str
    result: Optional[str] = None
    executed: bool = False


# In-memory storage
agents: Dict[str, Agent] = {}
commands: Dict[str, List[Command]] = {}
storage_lock = asyncio.Lock()


@app.post("/agents/register")
async def register_agent(agent: Agent):
    async with storage_lock:
        if agent.id in agents:
            raise HTTPException(status_code=400, detail="Agent already registered.")
        agents[agent.id] = agent
        commands[agent.id] = []
    return {"message": f"Agent {agent.name}, id:{agent.id} registered successfully."}


@app.post("/commands/send/{agent_id}")
async def send_command(agent_id: str, command: str):
    async with storage_lock:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found.")
        cmd = Command(id=str(uuid.uuid4()), command=command)
        commands[agent_id].append(cmd)
    return {
        "messege": f"Command'{command} sent to agent {agent_id}",
        "command_id": cmd.id,
    }


@app.get("/commands/{agent_id}")
async def get_pending_command(agent_id: str):
    async with storage_lock:
        if agent_id not in commands:
            raise HTTPException(status_code=404, detail="Agent not found.")
        for cmd in commands[agent_id]:
            if not cmd.executed:
                return cmd
    return {"message": "No pending commands."}


@app.post("/responses/{agent_id}/{command_id}")
async def post_response(agent_id: str, command_id: str, result: str):
    async with storage_lock:
        if agent_id not in commands:
            raise HTTPException(status_code=404, detail="Agent not found.")
        for cmd in commands[agent_id]:
            if cmd.id == command_id:
                cmd.result = result
                cmd.executed = True
                return {"message": "Result received.", "result": result}
    raise HTTPException(status_code=404, detail="Command not found.")


@app.get("/responses/{agent_id}")
async def get_responses(agent_id: str):
    async with storage_lock:
        if agent_id not in commands:
            raise HTTPException(status_code=404, detail="Agent not found.")
    return [cmd for cmd in commands[agent_id] if cmd.executed]
