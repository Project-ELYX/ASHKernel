import subprocess
import time
import os
import signal

class EngineManager:
    def __init__(self):
        # Path to the binary in your project root
        self.bin = "./vllm" 
        self.model = os.getenv("LOCAL_MODEL_PATH", "./models/Hermes-3-8B")
        self.use_local = os.getenv("USE_LOCAL_INFERENCE", "false").lower() == "true"
        self.process = None

    def start(self):
        if not self.use_local:
            print("[ENGINE] Local engine bypassed. Using Cloud Umbilical.")
            return

        print(f"[ENGINE] Spawning local brain from binary: {self.bin}")
        # Command optimized for 12GB VRAM
        cmd = [
            self.bin, "serve", self.model,
            "--gpu-memory-utilization", "0.85", # Leaves 2GB for Debian/System
            "--max-model-len", "8192",
            "--enable-auto-tool-choice",
            "--tool-call-parser", "hermes" # Specifically for Hermes models
        ]
        
        # Start in a new process group so it doesn't die if main.py blips
        self.process = subprocess.Popen(cmd, preexec_fn=os.setsid)
        print("[ENGINE] Loading Safetensors... this usually takes 15-30s.")
        time.sleep(20) 

    def stop(self):
        if self.process:
            print("[ENGINE] Terminating local vLLM process group.")
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)