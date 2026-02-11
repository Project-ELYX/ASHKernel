import subprocess
import json
import os
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

    # --- TOOL 1: ADD TO WHITELIST ---
    def update_merc_whitelist(category: str, entry: str):
        """
        Adds a process name, IP address, or directory to the Merc Whitelist.
        Args:
            category: Must be 'processes', 'ips', or 'directories'.
            entry: The specific value to whitelist (e.g. 'Peace.exe').
        """
        whitelist = load_whitelist()
        if category in whitelist:
            if entry not in whitelist[category]:
                whitelist[category].append(entry)
                with open(WHITELIST_PATH, "w") as f:
                    json.dump(whitelist, f, indent=2)
                return f"PROCESSED: {entry} added to {category} whitelist. Target is now an ally."
            return f"INFO: {entry} is already on the whitelist."
        return f"ERROR: Invalid category '{category}'."

    # --- TOOL 2: NEUTRALIZE TARGET ---
    def execute_neutralization(target_name: str, pid: int = None, file_path: str = None):
        """
        Neutralizes a threat. Checks the Merc Whitelist and Safety Lock first.
        """
        if SAFETY_LOCKED:
            return "ACCESS DENIED: Master Safety Lock is ENGAGED. Flip the switch in merc_config.py."

        whitelist = load_whitelist()
        
        # Check Whitelist
        if target_name in whitelist["processes"] or (file_path and any(d in file_path for d in whitelist["directories"])):
            return f"ABORTED: '{target_name}' is a confirmed ally. I will not fire."

        results = []
        try:
            if pid:
                subprocess.check_output(["powershell.exe", "-Command", f"Stop-Process -Id {pid} -Force"], stderr=subprocess.STDOUT)
                results.append(f"PID {pid} ({target_name}) neutralized.")
            
            if file_path:
                subprocess.check_output(["powershell.exe", "-Command", f"Remove-Item -Path '{file_path}' -Force"], stderr=subprocess.STDOUT)
                results.append(f"Source file vaporized.")
                
            return "\n".join(results) if results else "No targets identified."
            
        except Exception as e:
            return f"FAILURE: {str(e)}"

    # Register both tools
    if kernel.brain:
        kernel.brain.register_tool(update_merc_whitelist)
        kernel.brain.register_tool(execute_neutralization)