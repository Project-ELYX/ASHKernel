import subprocess
import time
import os
import signal
import platform
import sys

class EngineManager:
    def __init__(self, cmd_override=None, model_path=None):
        self.cmd = cmd_override or [sys.executable, "-m", "vllm.entrypoints.openai.api_server"]
        self.model = model_path or os.getenv("LOCAL_MODEL_PATH", "./models/Hermes-3-8B")
        self.use_local = os.getenv("USE_LOCAL_INFERENCE", "false").lower() == "true"
        self.process = None

    def start(self):
        if not self.use_local: return

        print(f"[ENGINE] Spawning local brain with emergency VRAM caps...")
        
        env = os.environ.copy()
        env["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
        
        full_cmd = self.cmd + [
            "--model", self.model,
            "--gpu-memory-utilization", "0.85", # Bumped back up slightly to allow more KV cache
            "--max-model-len", "2048",         # Drastically reduced to fit KV cache in 0.44GiB
            "--enforce-eager",                 # Disables CUDA graphs to save ~1GB overhead
            "--enable-auto-tool-choice",
            "--tool-call-parser", "hermes"
        ]
        
        flags = 0
        if platform.system() == "Windows":
            flags = subprocess.CREATE_NEW_PROCESS_GROUP
        
        self.process = subprocess.Popen(
            full_cmd, 
            env=env,
            creationflags=flags, 
            start_new_session=(platform.system() != "Windows")
        )
        
        print("[ENGINE] Attempting VRAM loading... (2048 Context Cap)")
        time.sleep(20) 

    def stop(self):
        if self.process:
            if platform.system() == "Windows":
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            else:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)