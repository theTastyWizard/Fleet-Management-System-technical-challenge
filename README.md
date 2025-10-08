#Architecture
## API server
- Handle requests for sending commands 
- Send commands to specific agents
- get response from agents

## Remote agent
- Get commands and execute them
- simulate command executing and send response back to server

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


# Possible Improvements
- Develop a concrete set of commands and use a command design pattern if the project
requires new commands to be added frequently
- Connecting to persistant storage (DB of choice)
- Use the persistant storage to store the command queue and add re-connect logic to agents
- Add proper client authentication ex. JWT in websocket headers
- Add tracking of connected clients with up-times and integration with dashboards
- Containerize for portability using docker/kuberneties/deb/nix packages
- ability to update code on clients remotely



