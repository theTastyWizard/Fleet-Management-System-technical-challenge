import uuid
import requests
import time

SERVER_URL = "http://127.0.0.1:8000"
AGENT_ID = str(uuid.uuid4())
AGENT_NAME = "Test1"


def register():
    r = requests.post(
        f"{SERVER_URL}/agents/register", json={"id": AGENT_ID, "name": AGENT_NAME}
    )
    print("Agent registered:", r.json())


def execute_cmd(command):
    print(f"Executing command: {command}")
    results = f"Executed '{command}' successfully."
    return results


def send_result(cmd_id, result):
    r = requests.post(f"{SERVER_URL}/responses/{AGENT_ID}/{cmd_id}", params = {"result": result})
    print("Sent result:", r.json())


def poll():
    while True:
        r = requests.get(f"{SERVER_URL}/commands/{AGENT_ID}")
        data = r.json()
        if "command" in data:
            cmd = data["command"]
            cmd_id = data["id"]
            result = execute_cmd(cmd)
            time.sleep(1)
            send_result(cmd_id, result)
        else:
            print("No commands. Sleeping")
            time.sleep(5)


if __name__ == "__main__":
    register()
    poll()
