# Fleet Management System 
A minimal yet extensible **Fleet Management System** built with **FastAPI**, **aiohttp**, and **WebSockets**
simulating real-time communication between a central API Server and multiple Remote Agents.

This project is for a techical challenge demonstrating backend architecture, async programming and client-server system design

## features:
- fastAPI-based API server with async endpoints  
- websocket communication for instant command delivery  
- resilient agent clients that reconnect automatically  
- queued commands delivered after reconnection

## API server
- Handle requests for sending commands 
- Send commands to specific agents
- send commands to multiple and all agents
- get response from agents

## Remote agent
- register with API server
- receive commands instantly (with websocket) and execute them
- send results back asynchronously
- automatically reconnect and execute pending commands if disconnected

## Language choice
- Python for ease of use and familiarity
- Would perhaps use Go or Rust for a larger project do to memory management and builtin
concurrency 

## Development
- started with getting the basics working: python http server and agent using get and
post request where the agent was constantly polling the server for commands
- researched dependencies and decided on FastApi for the performance (see benchmarks on their repo), good documentation and ease of use.
- First improvement was making the agent and servers asynchronous where applicable using
the asyncio and aiohttp packages. Delivering scalability and performance improvements.
Added command queue so agent can check if they have executed all their commands.
- To remove the need for the server polling, I added a WebSocket connection to increase
speed of sending commands significantly and having the connection be bidirectional and
kept alive by reusage of established connection channel. Added storage of push status for
commands
- Added better concurrency with task gathering for multiple commands
- Added reconnect logic for agents that have lost connection, so that commands are stored
and executed when reconnected


## Possible Improvements
- Develop a concrete set of commands and use a command design pattern if the project
requires new commands to be added frequently
- Replace in-memory storage with persistant storage (DB of choice)
- Add proper client authentication ex. JWT in websocket headers or API key validation
- Add tracking of connected clients with up-times, latency
- integration with dashboards to vizualize fleet status
- Containerize for portability using docker/kuberneties/deb/nix packages
- ability to update code on clients remotely

## How it works
- 1. Agent registers with the server using an HTTP request.
- 2. Agent opens a WebSocket connection to /ws/{agent_id}.
- 3. Server pushes commands instantly to connected agents.
- 4. Offline agents get queued commands when they reconnect.
- 5. Agents execute commands asynchronously and POST results back.
- 6. Server stores responses retrievable via /responses/{agent_id}.

## Installation
This project uses **[uv](https://github.com/astral-sh/uv)** for fast Python environment and dependency management.

### Clone the repo
```bash
git clone https://github.com/theTastyWizard/Fleet-Management-System-technical-challenge
cd Fleet-Management-System-technical-challenge
``````

### Create and sync environment
```bash
uv sync
```

This  will create virtual env and install dependencies listed in pyproject.toml

### activate the environment 
```bash
source .venv/bin/activate   # (Linux/macOS)
# or
.venv\Scripts\activate      # (Windows)
```

## Usage

### run API server
```bash
fastapi run ws-async-server.py
# or in dev
fastapi dev ws-async-server.py
```
### start an agent
```bash
python ws-async-agent.py
```

### send command to specific agent
Replacing {agent_id} with the actual id and {command} with a string for a command (only simulated execution)
```bash
curl -X POST "http://127.0.0.1:8000/commands/send/{agent_id}?command={command}"
```

### send command to all agents
```bash
 curl -X POST "http://127.0.0.1:8000/commands/send_to_all?command={command}"
```

### Send command to a subset of agents
Replacing {agent_id}s with the actual ids and {command} with a string for a command (only simulated execution)
```bash
 curl -X POST "http://127.0.0.1:8000/commands/send_multiple?command={command}" \
      -H "Content-Type: application/json" \
      -d '["{agent-1-uuid}", "{agent-2-uuid}"]'
```

### view responses
Replacing {agent_id} with the actual id

```bash
curl "http://127.0.0.1:8000/responses/{agent_id}"
```

###  Scaling server with workers
To use more workers and scale the server and usage multiple cores your can use the
--worker flag that comes from the uvicorn backend

```bash
fastapi run --workers 4 ws-async-server.py
``````

## Author
[email](mattipatti1998@gmail.com)
[linkedin](https://www.linkedin.com/in/sigur%C3%B0ur-marteinn-lyngberg-sigur%C3%B0sson-1344b0335)
