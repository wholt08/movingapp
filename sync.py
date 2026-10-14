#!/usr/bin/env python3
"""
Moving Command Center CLI Sync Utility
Syncs local data/move_data.json with Firebase Realtime Database.
Allows Antigravity, Claude Code, or terminal commands to push/pull moving plan state.
"""

import sys
import os
import json
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "data", "move_data.json")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "firebase_config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {CONFIG_FILE}: {e}")
        return None

def get_database_url():
    config = load_config()
    if config and "databaseURL" in config and config["databaseURL"]:
        url = config["databaseURL"].rstrip('/')
        return url
    env_url = os.environ.get("FIREBASE_DB_URL")
    if env_url:
        return env_url.rstrip('/')
    return None

def pull():
    db_url = get_database_url()
    if not db_url:
        print("[!] Firebase database URL not configured.")
        print(f"    Please add your 'databaseURL' to {CONFIG_FILE}")
        return False

    url = f"{db_url}/moveData.json"
    print(f"[*] Pulling latest moving plan from {url} ...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MovingAppSync/1.0'})
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if not data:
                    print("[!] Remote database is empty. Push local data first.")
                    return False
                os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
                with open(DATA_FILE, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"[✓] Successfully updated {DATA_FILE} with latest cloud data!")
                return True
    except Exception as e:
        print(f"[!] Error pulling from Firebase: {e}")
        return False

def push():
    db_url = get_database_url()
    if not db_url:
        print("[!] Firebase database URL not configured.")
        print(f"    Please add your 'databaseURL' to {CONFIG_FILE}")
        return False

    if not os.path.exists(DATA_FILE):
        print(f"[!] {DATA_FILE} not found!")
        return False

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    url = f"{db_url}/moveData.json"
    print(f"[*] Pushing local plan ({DATA_FILE}) to {url} ...")
    try:
        payload = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method='PUT', headers={
            'Content-Type': 'application/json',
            'User-Agent': 'MovingAppSync/1.0'
        })
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("[✓] Successfully synced to Firebase! All phones and browsers will update immediately.")
                return True
    except Exception as e:
        print(f"[!] Error pushing to Firebase: {e}")
        return False

def status():
    db_url = get_database_url()
    print("=== Moving App Sync Status ===")
    print(f"Local Data File : {DATA_FILE} ({'Exists' if os.path.exists(DATA_FILE) else 'Missing'})")
    print(f"Config File     : {CONFIG_FILE} ({'Exists' if os.path.exists(CONFIG_FILE) else 'Missing'})")
    print(f"Database URL    : {db_url or 'NOT CONFIGURED'}")

if __name__ == "__main__":
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if cmd == "pull":
        pull()
    elif cmd == "push":
        push()
    elif cmd == "status":
        status()
    else:
        print("Usage: python3 sync.py [pull | push | status]")
