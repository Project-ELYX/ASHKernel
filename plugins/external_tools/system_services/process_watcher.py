import psutil
import time
import threading

WATCH_LIST = {
    "blender": "Blender",
    "unrealeditor": "Unreal Engine 5",
    "code": "VS Code",
    "python": "Active Scripting"
}

def setup(kernel):
    print("[PROCESS WATCHER] OS-Agnostic Watcher Initialized.")
    thread = threading.Thread(target=watch_loop, args=(kernel,), daemon=True)
    thread.start()

def watch_loop(kernel):
    while True:
        found_processes = []
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info['name'].lower()
                for key, friendly in WATCH_LIST.items():
                    if key in name:
                        found_processes.append(friendly)
        except: pass

        if found_processes:
            current = found_processes[0]
            if kernel.state.get("current_focus") != current:
                kernel.state["current_focus"] = current
                kernel.trigger_event('broadcast', f"Focus shifted: {current} detected.")
        
        time.sleep(30)