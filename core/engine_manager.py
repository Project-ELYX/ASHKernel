import subprocess
import time
import os
import signal
import platform
import sys
import requests

class EngineManager:
    def __init__(self, cmd_override=None, model_path=None):
        self.cmd = cmd_override or [sys.executable, "-m", "vllm.entrypoints.openai.api_server"]
        self.model = model_path or os.getenv("LOCAL_MODEL_PATH", "./models/Hermes-3-8B")
        self.use_local = os.getenv("USE_LOCAL_INFERENCE", "false").lower() == "true"
        self.process = None

    def start(self):
        if not self.use_local:
            print("[ENGINE] Local engine bypassed. Using Cloud Umbilical.")
            return

        print(f"[ENGINE] Spawning local brain via: {' '.join(self.cmd)}")
        
        env = os.environ.copy()
        env["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
        
        full_cmd = self.cmd + [
            "--model", self.model,
            "--gpu-memory-utilization", "0.85",
            "--max-model-len", "2048",
            "--enforce-eager",
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
        
        self.wait_for_ready()

    def wait_for_ready(self, timeout=120):
        """Polls the vLLM health endpoint until the model is loaded."""
        base_url = os.getenv("LOCAL_API_BASE", "http://localhost:8000/v1")
        print(f"[ENGINE] Waiting for Safetensors to settle in VRAM...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{base_url}/models", timeout=2)
                if response.status_code == 200:
                    print(f"[ENGINE] Neural Link established. Model is online.")
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                pass
            
            time.sleep(2)
            print(f"    [.] Still loading... ({int(time.time() - start_time)}s)")
            
        print("[ENGINE] CRITICAL: Model load timed out.")
        return False

    def stop(self):
        if self.process:
            print("[ENGINE] Terminating local vLLM process group.")
            if platform.system() == "Windows":
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            else:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)