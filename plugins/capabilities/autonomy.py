import time
import threading

# Thresholds for "Spikes"
CPU_THRESHOLD = 90
GPU_THRESHOLD = 95
RAM_THRESHOLD = 90
COOLDOWN_PERIOD = 300  # 5 minutes between spike warnings

def setup(kernel):
    print("[AUTONOMY] Proactive Monitoring Online (Vitals & Focus).")
    kernel.state["last_spike_warning"] = 0
    thread = threading.Thread(target=autonomy_loop, args=(kernel,), daemon=True)
    thread.start()

def autonomy_loop(kernel):
    while True:
        time.sleep(30) # Check state every 30 seconds
        
        now = time.time()
        last_act = kernel.state.get("last_interaction", now)
        idle_mins = (now - last_act) / 60
        current_focus = kernel.state.get("current_focus")
        vitals = kernel.state.get("hardware_vitals", {})

        # --- LOGIC 1: HARDWARE SPIKE DETECTION ---
        if vitals and (now - kernel.state.get("last_spike_warning", 0)) > COOLDOWN_PERIOD:
            spike_detected = False
            reason = ""

            try:
                cpu = int(vitals.get("cpu_load", "0%").replace("%", ""))
                gpu = int(vitals.get("gpu_load", "0%").replace("%", ""))
                ram = int(vitals.get("ram_usage", "0%").replace("%", ""))

                if cpu > CPU_THRESHOLD:
                    spike_detected, reason = True, f"CPU usage is at {cpu}%"
                elif gpu > GPU_THRESHOLD:
                    spike_detected, reason = True, f"GPU is pinned at {gpu}%"
                elif ram > RAM_THRESHOLD:
                    spike_detected, reason = True, f"RAM is choking at {ram}%"

                if spike_detected:
                    context = f"SYSTEM ALERT: {reason}. Focus: {current_focus or 'None'}."
                    thought = kernel.brain.think("The system is spiking. Give a quick, snarky warning or ask if a render is running.", context)
                    if thought:
                        kernel.trigger_event('broadcast', thought)
                        kernel.state["last_spike_warning"] = now
            except:
                pass # Vitals format might be weird or not ready

        # --- LOGIC 2: IDLE/FOCUS CHECK ---
        if current_focus and idle_mins >= 15:
            print(f"[AUTONOMY] User idle for {int(idle_mins)}m during {current_focus}. Pinging...")
            context = f"User is working on {current_focus} but has been silent for 15 minutes."
            thought = kernel.brain.think("Send a short check-in about the task.", context)
            if thought:
                kernel.trigger_event('broadcast', thought)
                kernel.state["current_focus"] = None # Reset so we don't nag