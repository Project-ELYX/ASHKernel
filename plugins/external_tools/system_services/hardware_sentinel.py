import subprocess
import threading
import time
import psutil
import platform

def setup(kernel):
    print("[SENTINEL] Hardware Monitoring Online. OS: " + platform.system())
    
    def check_vitals_tool():
        """Returns the current CPU, GPU, and RAM status of the host."""
        return kernel.state.get("hardware_vitals", "Stats not ready yet.")

    if kernel.brain:
        kernel.brain.register_tool(check_vitals_tool)

    thread = threading.Thread(target=hardware_loop, args=(kernel,), daemon=True)
    thread.start()

def get_gpu_stats():
    """Cross-platform check for NVIDIA GPU stats."""
    try:
        # Querying nvidia-smi directly (works on both Linux and Windows)
        cmd = ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
        gpu_load, gpu_temp = output.split(",")
        return f"{gpu_load.strip()}%", f"{gpu_temp.strip()}°C"
    except Exception:
        return "0%", "0°C"

def hardware_loop(kernel):
    while True:
        # Use psutil for native cross-platform CPU and RAM stats
        cpu_load = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        gpu_load, gpu_temp = get_gpu_stats()
        
        stats = {
            "cpu_load": f"{cpu_load}%",
            "ram_usage": f"{ram.percent}%",
            "gpu_load": gpu_load,
            "gpu_temp": gpu_temp
        }
        
        kernel.state["hardware_vitals"] = stats
        
        # --- CHAOS LOGIC ---
        if gpu_temp != "0°C":
            temp_val = int(gpu_temp.replace("°C", ""))
            if temp_val > 85:
                kernel.trigger_event('broadcast', f"CRITICAL: GPU is at {temp_val}°C. Pull back or we're going to melt the silicon.")
        
        time.sleep(15)