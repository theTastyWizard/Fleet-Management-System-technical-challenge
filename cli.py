import asyncio
import typer
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live


app = typer.Typer(help="Fleet management CLI - for testing and demoing")

SERVER_URL = "http://127.0.0.1:8000"
REFRESH_INTERVAL = 3  # seconds between updates
console = Console()


# helper to handle and pretty print json response
def handle_response(r):
    try:
        data = r.json()
    except Exception:
        console.print("[red]Error parsing response[/red]")
        return
    if r.status_code >= 400:
        console.print(f"[red]Error {r.status_code}:[/red] {data.get('detail', data)}")
    else:
        console.print_json(data=data)


@app.command("list-agents")
def list_reg_agents():
    """List registered agents."""
    r = requests.get(f"{SERVER_URL}/agents")
    if r.status_code != 200:
        handle_response(r)
        return
    agents = r.json()
    if not agents:
        console.pritn("[yellow]No registered agents.[/yellow]")
        return
    table = Table(title="Registered agents")
    table.add_column("Agent ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="white")
    for a in agents:
        table.add_row(a["id"], a["name"])
    console.print(table)


@app.command()
def status():
    """Show simple system status and connected agenst"""
    r = requests.get(f"{SERVER_URL}/status")
    if r.status_code != 200:
        handle_response(r)
        return
    data = r.json()

    console.print("\n[bold cyan]System Status[/bold cyan]")
    console.print(f"Total Agents:       [green]{data['total_agents']}[/green]")
    console.print(f"Connected Agents:   [green]{data['connected_agents']}[/green]")
    console.print(f"Queued Commands:    [yellow]{data['queued_commands']}[/yellow]")
    console.print(f"Executed Commands:  [cyan]{data['executed_commands']}[/cyan]\n")

    if data["connected_ids"]:
        table = Table(title="Connected Agents")
        table.add_column("Agent ID", style="cyan")
        for agent_id in data["connected_ids"]:
            table.add_row(agent_id)
        console.print(table)
    else:
        console.print("[dim]No agents currently connected.[/dim]")


@app.command()
def send(agent_id: str, command: str):
    """Send a command to a specific agent using id."""
    r = requests.post(
        f"{SERVER_URL}/commands/send/{agent_id}", params={"command": command}
    )
    handle_response(r)


@app.command()
def send_to_all(command: str):
    """Send a command to all connected agents."""
    r = requests.post(f"{SERVER_URL}/commands/send_to_all", params={"command": command})
    handle_response(r)


@app.command()
def send_multiple(command: str, agent_ids: str):
    """
    Send a command to multiple agents.
    Example:
        python cli.py send_multiple "diagnostic" "id1,id2,id3"
    """
    ids = [a.strip() for a in agent_ids.split(",")]
    r = requests.post(
        f"{SERVER_URL}/commands/send_multiple",
        params={"command": command},
        json=ids,
        headers={"Content-Type": "application/json"},
    )
    handle_response(r)


@app.command()
def responses(agent_id: str):
    """Fetch all executed command responses from an agent."""
    r = requests.get(f"{SERVER_URL}/responses/{agent_id}")
    if r.status_code == 200:
        data = r.json()
        if not data:
            console.print("[yellow]No responses yet.[/yellow]")
            return
        table = Table(title=f"Responses for Agent {agent_id}")
        table.add_column("Command ID", style="cyan")
        table.add_column("Command", style="white")
        table.add_column("Result", style="green")
        for cmd in data:
            table.add_row(cmd["id"], cmd["command"], cmd.get("result", "—"))
        console.print(table)
    else:
        handle_response(r)


@app.command()
def dashboard():
    """
    Live-updating dashboard showing connected agents and system metrics.
    Refreshes every few seconds.
    """
    console.print("[bold cyan]Starting Fleet Management Dashboard...[/bold cyan]")
    console.print(
        f"[dim]Refreshing every {
            REFRESH_INTERVAL
        } seconds. Press Ctrl+C to exit.[/dim]\n"
    )

    try:
        with Live(refresh_per_second=2, console=console, screen=True) as live:
            while True:
                # Fetch system status
                try:
                    status_res = requests.get(f"{SERVER_URL}/status", timeout=5)
                    agents_res = requests.get(f"{SERVER_URL}/agents", timeout=5)
                    status_data = status_res.json() if status_res.ok else {}
                    agents_data = agents_res.json() if agents_res.ok else []
                except Exception as e:
                    live.update(
                        Panel(
                            f"[red]Error connecting to server:[/red] {e}",
                            title="Connection Error",
                        )
                    )
                    asyncio.sleep(REFRESH_INTERVAL)
                    continue

                # Build tables
                main_table = Table(title="System Status", expand=True)
                main_table.add_column("Metric", style="cyan", justify="right")
                main_table.add_column("Value", style="green")
                main_table.add_row(
                    "Total Agents", str(status_data.get("total_agents", "?"))
                )
                main_table.add_row(
                    "Connected Agents", str(status_data.get("connected_agents", "?"))
                )
                main_table.add_row(
                    "Queued Commands", str(status_data.get("queued_commands", "?"))
                )
                main_table.add_row(
                    "Executed Commands", str(status_data.get("executed_commands", "?"))
                )

                agent_table = Table(title="Registered Agents", expand=True)
                agent_table.add_column("Agent ID", style="white")
                agent_table.add_column("Name", style="cyan")
                agent_table.add_column("Status", style="green")
                connected_ids = set(status_data.get("connected_ids", []))
                for a in agents_data:
                    status = "🟢 online" if a["id"] in connected_ids else "🔴 offline"
                    agent_table.add_row(a["id"], a["name"], status)

                # Combine tables
                dashboard_panel = Panel.fit(
                    main_table,
                    title="Fleet Management System",
                    subtitle="[dim]API Server: 127.0.0.1:8000[/dim]",
                )

                # Display stacked layout
                layout = Table.grid(expand=True)
                layout.add_row(dashboard_panel)
                layout.add_row(agent_table)
                live.update(layout)

                # Wait for next update
                asyncio.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Dashboard stopped by user.[/bold yellow]")


if __name__ == "__main__":
    app()
