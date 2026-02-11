import os
import psutil
import json
from core.merc_config import SAFETY_LOCKED

WHITELIST_PATH = "data/merc_whitelist.json"

def load_whitelist():
    if os.path.exists(WHITELIST_PATH):
        try:
            with open(WHITELIST_PATH, "r") as f:
                return json.load(f)
        except:
            pass
    return {"processes": [], "ips": [], "directories": []}

def setup(kernel):
    print(f"[MERC] Tactical Tools Loaded. Safety Lock: {'ON' if SAFETY_LOCKED else 'OFF'}")

    def update_merc_whitelist(category: str, entry: str):
        whitelist = load_whitelist()
        if category in whitelist:
            if entry not in whitelist[category]:
                whitelist[category].append(entry)
                with open(WHITELIST_PATH, "w") as f:
                    json.dump(whitelist, f, indent=2)
                return f"PROCESSED: {entry} added to {category} whitelist."
            return f"INFO: {entry} is already on the whitelist."
        return f"ERROR: Invalid category '{category}'."

    def execute_neutralization(target_name: str, pid: int = None, file_path: str = None):
        if SAFETY_LOCKED:
            return "ACCESS DENIED: Master Safety Lock is ENGAGED."

        whitelist = load_whitelist()
        
        # Check Whitelist
        if target_name in whitelist["processes"]:
            return f"ABORTED: '{target_name}' is a confirmed ally."

        results = []
        try:
            if pid:
                p = psutil.Process(pid)
                p.terminate() # cleaner than Stop-Process
                results.append(f"PID {pid} ({target_name}) neutralized.")
            
            if file_path:
                if os.path.exists(file_path):
                    os.remove(file_path) # OS-agnostic vaporization
                    results.append(f"Source file {file_path} vaporized.")
                
            return "\n".join(results) if results else "No targets identified."
            
        except Exception as e:
            return f"FAILURE: {str(e)}"

    if kernel.brain:
        kernel.brain.register_tool(update_merc_whitelist)
        kernel.brain.register_tool(execute_neutralization)