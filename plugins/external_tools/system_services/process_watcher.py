import os
import subprocess
import platform
import time
import threading

# List of all processes to watch for
WATCH_LIST = {
    "blender.exe": "Blender (Windows)",
    "blender": "Blender (Linux)",
    "UnrealEditor.exe": "Unreal Engine 5 Editor (Windows)",
    "Code - Insiders.exe": "Visual Studio Code Insiders (Windows)",
    "Steam.exe": "Procrastinating with Steam Games"
}

def setup(kernel):
    print("[PROCESS WATCHER] Process Watcher Initialized. Monitoring for active software...")
    thread = threading.Thread(target=watch_loop, args=(kernel,), daemon=True)
    thread.start()

def is_wsl():
    return "microsoft" in platform.uname().release.lower()

def get_windows_processes():
    try:
        output = subprocess.check_output(["tasklist.exe"], stderr=subprocess.STDOUT).decode('utf-8', 'ignore')
        return output.lower()
    except Exception:
        return ""
    
def watch_loop(kernel):
    while True:
        found_processes = []

        # 1. Check windows side if in WSL
        if is_wsl():
            win_procs = get_windows_processes()
            for proc, friendly_name in WATCH_LIST.items():
                if proc.lower() in win_procs:
                    found_processes.append(friendly_name)

        # 2. Check native side (Linux/Standard Windows Python)
        import psutil
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info['name'].lower()
                for watch_item, friendly_name in WATCH_LIST.items():
                    if watch_item.lower() == name:
                        if friendly_name not in found_processes:
                            found_processes.append(friendly_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        # 3. Logic: If a process is found, update the kernel state
        if found_processes:
            current_app = found_processes[0]

            # If discovering new focus, trigger event or set focus
            if kernel.state.get("current_focus") != current_app:
                print(f"[PROCESS WATCHER] New focus detected: {current_app}")
                kernel.state["current_focus"] = current_app
                kernel.state["last_interaction"] = time.time()

                # Trigger event so ASH mentions it in chat
                kernel.trigger_event('broadcast', f"I see you opened {current_app}.")

        time.sleep(30)