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

# Ensure stdout supports UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "data", "move_data.json")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "firebase_config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
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
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"[✓] Successfully updated {DATA_FILE} with latest cloud data!")
                return True
    except Exception as e:
        print(f"[!] Error pulling from Firebase: {e}")
        return False

def fetch_remote():
    db_url = get_database_url()
    if not db_url:
        return None
    url = f"{db_url}/moveData.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MovingAppSync/1.0'})
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"[*] Note: Could not fetch remote data for merge: {e}")
    return None

def smart_merge(local, remote):
    """
    Intelligently merges remote cloud state into local data.
    Ensures that any task marked 'Done' on a phone/browser is preserved
    and not accidentally overwritten by stale local status.
    """
    if not remote or not isinstance(remote, dict):
        return local

    merged = json.loads(json.dumps(local)) # deepcopy

    # 1. Merge Tasks
    if "tasks" in merged and isinstance(merged["tasks"], list) and "tasks" in remote and isinstance(remote["tasks"], list):
        remote_tasks_by_id = {t["id"]: t for t in remote["tasks"] if isinstance(t, dict) and "id" in t}
        for t in merged["tasks"]:
            if not isinstance(t, dict): continue
            rt = remote_tasks_by_id.get(t.get("id"))
            if rt:
                # If remote marked it Done, keep it Done
                if rt.get("status") == "Done":
                    t["status"] = "Done"

    # 2. Merge Home Repairs
    if "homeRepairs" in merged and isinstance(merged["homeRepairs"], list) and "homeRepairs" in remote and isinstance(remote["homeRepairs"], list):
        remote_repairs = {r["id"]: r for r in remote["homeRepairs"] if isinstance(r, dict) and "id" in r}
        for r in merged["homeRepairs"]:
            if not isinstance(r, dict): continue
            rr = remote_repairs.get(r.get("id"))
            if rr and rr.get("status") == "Done":
                r["status"] = "Done"

    # 3. Merge Packing Lists
    if "packingLists" in merged and isinstance(merged["packingLists"], dict) and "packingLists" in remote and isinstance(remote["packingLists"], dict):
        for container in ["pod", "subaru"]:
            if container in merged["packingLists"] and container in remote["packingLists"]:
                r_items = {it["id"]: it for it in remote["packingLists"][container] if isinstance(it, dict) and "id" in it}
                for it in merged["packingLists"][container]:
                    if not isinstance(it, dict): continue
                    rit = r_items.get(it.get("id"))
                    if rit and rit.get("packed") is True:
                        it["packed"] = True

    # 4. Merge Marketplace
    if "marketplace" in merged and isinstance(merged["marketplace"], list) and "marketplace" in remote and isinstance(remote["marketplace"], list):
        remote_mp = {m["id"]: m for m in remote["marketplace"] if isinstance(m, dict) and "id" in m}
        for m in merged["marketplace"]:
            if not isinstance(m, dict): continue
            rm = remote_mp.get(m.get("id"))
            if rm and rm.get("status") in ["Sold", "Picked up", "Rehomed"]:
                m["status"] = rm["status"]

    return merged

def push(force=False):
    db_url = get_database_url()
    if not db_url:
        print("[!] Firebase database URL not configured.")
        print(f"    Please add your 'databaseURL' to {CONFIG_FILE}")
        return False

    if not os.path.exists(DATA_FILE):
        print(f"[!] {DATA_FILE} not found!")
        return False

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not force:
        print("[*] Checking remote cloud state to prevent overwriting active phone/browser progress...")
        remote_data = fetch_remote()
        if remote_data:
            data = smart_merge(data, remote_data)
            # Write merged back to disk
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("[✓] Smart merge complete: user completed items safely preserved.")

    url = f"{db_url}/moveData.json"
    print(f"[*] Pushing plan ({DATA_FILE}) to {url} ...")
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
    force_flag = "--force" in sys.argv or "-f" in sys.argv
    if cmd == "pull":
        pull()
    elif cmd == "push":
        push(force=force_flag)
    elif cmd == "status":
        status()
    else:
        print("Usage: python3 sync.py [pull | push [--force] | status]")
