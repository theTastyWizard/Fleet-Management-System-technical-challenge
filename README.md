# Fleet Management System 
A minimal yet extensible **Fleet Management System** built with **FastAPI**, **aiohttp**, and **WebSockets**
simulating real-time communication between a central API Server and multiple Remote Agents.

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

# Language choice
- Python for ease of use and familiarity
- Would perhaps use Go or Rust for a larger project do to memory management and builtin
concurrency 

# Development
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


# Possible Improvements
- Develop a concrete set of commands and use a command design pattern if the project
requires new commands to be added frequently
- Connecting to persistant storage (DB of choice)
- Add proper client authentication ex. JWT in websocket headers or API key validation
- Add tracking of connected clients with up-times, latency
- integration with dashboards to vizualize fleet status
- Containerize for portability using docker/kuberneties/deb/nix packages
- ability to update code on clients remotely


## Installation
This project uses **[uv](https://github.com/astral-sh/uv)** for fast Python environment and dependency management.

### Clone the repo
