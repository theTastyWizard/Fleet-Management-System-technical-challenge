from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from fastapi.responses import JSONResponse
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
    pushed: bool = False
    executed: bool = False


# In-memory storage
agents: Dict[str, Agent] = {}
commands: Dict[str, List[Command]] = {}
connections: Dict[str, WebSocket] = {}
storage_lock = asyncio.Lock()


# registration using http
@app.post("/agents/register")
async def register_agent(agent: Agent):
    async with storage_lock:
        if agent.id in agents:
            raise HTTPException(status_code=400, detail="Agent already registered.")
        agents[agent.id] = agent
        commands[agent.id] = []
    return {"message": f"Agent {agent.name}, id:{agent.id} registered successfully."}


# websocket endpoint
@app.websocket("/ws/{agent_id}")
async def agent_ws(websocket: WebSocket, agent_id: str):
    await websocket.accept()
    connections[agent_id] = websocket
    print(f"Agent {agent_id} connected.")

    # on reconnect, send any pending commands again that havent been executed
    async with storage_lock:
        if agent_id in commands:
            pending = [cmd for cmd in commands[agent_id] if not cmd.executed]
            for cmd in pending:
                await websocket.send_json({"id": cmd.id, "command": cmd})
                print(f"Re-sent pending command '{cmd.command}' to agent {agent_id}")

    try:
        while True:
            # keep connection alive, also handle messages from agent
            msg = await websocket.receive_text()
            print(f"Received from {agent_id}: {msg}")
    except WebSocketDisconnect:
        # persistant tracking of agent connections
        print(f"Agent {agent_id} disconnected")
        del connections[agent_id]


# command sending to specific agent with http
@app.post("/commands/send/{agent_id}")
async def send_command(agent_id: str, command: str):
    async with storage_lock:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found.")
        cmd = Command(id=str(uuid.uuid4()), command=command)
        commands[agent_id].append(cmd)
        if agent_id in connections:
            await connections[agent_id].send_json({"id": cmd.id, "command": command})
            commands[agent_id][-1].pushed = True
            return {
                "message": f"Command '{command}' sent to agent {agent_id}",
                "pushed": True,
            }
        commands[agent_id][-1].pushed = False
        return JSONResponse(
            {"message": f"Agent {agent_id} offline. Command queued.", "pushed": False}
        )


# sending command to all agents with http
@app.post("/commands/send_to_all")
async def send_command_to_all(command: str):
    async with storage_lock:
        if not agents:
            raise HTTPException(status_code=404, detail="No agents registered.")
        for agent_id in agents:
            cmd = Command(id=str(uuid.uuid4()), command=command)
            # add to storage
            commands[agent_id].append(cmd)

        # gather tasks for better concurrency
        # push if connected
        send_tasks = []
        for agent_id, ws in connections.items():
            send_tasks.append(ws.send_json({"id": cmd.id, "command": command}))
            commands[agent_id][-1].pushed = True
        await asyncio.gather(*send_tasks, return_exceptions=True)

    return {"message": f"Sent '{command}' to {len(agents)} agents."}


# send command to multiple agents (list in JSON body)
@app.post("/commands/send_multiple")
async def send_command_multiple(
    agent_ids: List[str] = Body(...), command: str = "status"
):
    async with storage_lock:
        pushed_agents = []
        for agent_id in agent_ids:
            if agent_id not in agents:
                print(f"skipping unknown agent {agent_id}")
                continue
            cmd = Command(id=str(uuid.uuid4()), command=command)
            commands[agent_id].append(cmd)
            pushed_agents.append(agent_id)
            # push if connected
            if agent_id in connections:
                await connections[agent_id].send_json(
                    {"id": cmd.id, "command": command}
                )
    return {
        "message": f"Sent '{command}' to {len(pushed_agents)} agents",
        "agents": pushed_agents,
    }


# get registered agents
@app.get("/agents")
async def list_registered_agents():
    async with storage_lock:
        return list(agents.values())


# basic system status
@app.get("/status")
async def system_status():
    async with storage_lock:
        total_agents = len(agents)
        connected_agents = len(connections)
        queued_commands = sum(
            len([c for c in cmds if not c.executed]) for cmds in commands.values()
        )
        executed_commands = sum(
            len([c for c in cmds if c.executed]) for cmds in commands.values()
        )

    return {
        "total_agents": total_agents,
        "connected_agents": connected_agents,
        "queued_commands": queued_commands,
        "executed_commands": executed_commands,
        "connected_ids": list(connections.keys()),
    }


# agent response http post
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


# http get responses for executed cmds
@app.get("/responses/{agent_id}")
async def get_responses(agent_id: str):
    async with storage_lock:
        if agent_id not in commands:
            raise HTTPException(status_code=404, detail="Agent not found.")
    return [cmd for cmd in commands[agent_id] if cmd.executed]
