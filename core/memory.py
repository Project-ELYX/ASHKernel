import json
import os
from core.history import AshHistory

class AshMemory:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        
        self.memory_file = os.path.join(self.data_dir, "memory.json")
        self.prompt_file = os.path.join(self.data_dir, "system_prompt.md")
        self.instruct_file = os.path.join(self.data_dir, "instructions.md")
        # NEW: The Tool Manual
        self.tools_file = os.path.join(self.data_dir, "tools.md")
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.history = AshHistory(log_dir=os.path.join(self.data_dir, "logs"))

    def load_persona(self):
        """Combines System Prompt + Main Instructions + Tool Instructions"""
        try:
            with open(self.prompt_file, "r") as f:
                prompt = f.read()
            with open(self.instruct_file, "r") as f:
                instructions = f.read()
            
            # Load tools.md if it exists, otherwise use empty string
            tools_instruct = ""
            if os.path.exists(self.tools_file):
                with open(self.tools_file, "r") as f:
                    tools_instruct = f"\n\n### TOOL PROTOCOLS\n{f.read()}"
            
            return f"{prompt}\n\n{instructions}{tools_instruct}"
        except FileNotFoundError:
            return "SYSTEM ERROR: Persona files missing. Check data/ folder."

    def get_memory(self):
        """Reads the JSON memory file (Facts and Notes)"""
        if not os.path.exists(self.memory_file):
            return {}
        try:
            with open(self.memory_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[MEMORY] Error reading memory file: {e}")
            return {}

    def update_memory(self, key, value):
        """Allows the Agent to write a new fact to its memory.json"""
        data = self.get_memory()
        
        # If it's a list, append the new fact; otherwise, overwrite
        if key in data and isinstance(data[key], list):
            data[key].append(value)
        else:
            data[key] = value
            
        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[MEMORY] Fact stored: {key} -> {value}")