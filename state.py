import os, json

STATE_FILE = os.path.expanduser("~/.vebforvpn_state.json")

def save_last_key(key):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_key": key}, f)

def load_last_key():
    if not os.path.exists(STATE_FILE):
        return ""
    with open(STATE_FILE) as f:
        data = json.load(f)
        return data.get("last_key", "")
