import json
import os
from datetime import datetime

class AshHistory:
    def __init__(self, log_dir="data/logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        # One file per day to keep things neat
        self.current_log = os.path.join(self.log_dir, f"chat_{datetime.now().strftime('%Y-%m-%d')}.jsonl")

    def log(self, sender, message):
        """Appends a message to the daily log file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "content": message
        }
        with open(self.current_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_recent(self, limit=20):
        """Reads the last X lines and formats them for the Brain's context."""
        if not os.path.exists(self.current_log):
            return "No history recorded for today yet."
        
        try:
            with open(self.current_log, "r") as f:
                lines = f.readlines()
                recent_lines = lines[-limit:]
                formatted = []
                for line in recent_lines:
                    data = json.loads(line)
                    # Shorten timestamp for readability
                    time_str = data['timestamp'][11:16]
                    formatted.append(f"[{time_str}] {data['sender']}: {data['content']}")
                return "\n".join(formatted)
        except Exception as e:
            return f"Error reading logs: {e}"