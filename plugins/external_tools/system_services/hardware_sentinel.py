import subprocess
import threading
import time
import json

def setup(kernel):
    print("[SENTINEL] Hardware Monitoring Online. Checking vitals...")
    
    # 1. Register the tool so the Brain can check temps manually
    def check_vitals_tool():
        """Returns the current CPU, GPU, and RAM status of the Windows host."""
        return kernel.state.get("hardware_vitals", "Stats not ready yet.")

    if kernel.brain:
        kernel.brain.register_tool(check_vitals_tool)

    thread = threading.Thread(target=hardware_loop, args=(kernel,), daemon=True)
    thread.start()

def get_windows_stats():
    """Execute PowerShell commands to grab Windows host vitals."""
    # This script grabs: CPU %, Free RAM, and GPU Utilization (if NVIDIA)
    script = (
        "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty LoadPercentage; "
        "Get-CimInstance Win32_OperatingSystem | ForEach-Object { [math]::Round(($_.TotalVisibleMemorySize - $_.FreePhysicalMemory) / $_.TotalVisibleMemorySize * 100, 1) }; "
        "nvidia-smi --query-gpu=utilization.gpu,temperature.gpu --format=csv,noheader,nounits"
    )
    
    try:
        # Reaching out to the Windows host
        output = subprocess.check_output(["powershell.exe", "-Command", script], stderr=subprocess.STDOUT).decode('utf-8').splitlines()
        
        cpu = output[0] if len(output) > 0 else "0"
        ram = output[1] if len(output) > 1 else "0"
        gpu_stats = output[2].split(",") if len(output) > 2 else ["0", "0"]
        
        return {
            "cpu_load": f"{cpu}%",
            "ram_usage": f"{ram}%",
            "gpu_load": f"{gpu_stats[0].strip()}%",
            "gpu_temp": f"{gpu_stats[1].strip()}°C"
        }
    except Exception:
        return {"error": "Could not reach Windows sensors."}

def hardware_loop(kernel):
    while True:
        stats = get_windows_stats()
        kernel.state["hardware_vitals"] = stats
        
        # --- CHAOS LOGIC ---
        # If the GPU is over 85°C and we are in 'Blender' focus...
        if "gpu_temp" in stats and stats["gpu_temp"] != "0°C":
            temp = int(stats["gpu_temp"].replace("°C", ""))
            if temp > 85:
                # Trigger an emergency broadcast
                kernel.trigger_event('broadcast', f"EMERGENCY: Your GPU is hitting {temp}°C. Either stop the render or I'm calling the fire department.")
        
        time.sleep(15) # Refresh every 15 seconds