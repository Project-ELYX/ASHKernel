import psutil
import tempfile
import os
import json

def setup(kernel):
    print("[MERC] Threat Hunter Module Online. Scanning sectors...")

    def engage_merc_scan():
        """
        Runs a deep diagnostic sweep without OS-specific shell calls.
        Detects high-CPU ghosts and suspicious executables in temp dirs.
        """
        # 1. Detect 'Ghost' processes (High CPU but typically no UI)
        suspicious_procs = []
        for proc in psutil.process_iter(['name', 'cpu_percent', 'pid']):
            try:
                # Flagging processes using > 20% CPU that aren't your core tools
                if proc.info['cpu_percent'] > 20.0:
                    suspicious_procs.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # 2. Check Temp Directory for rogue executables
        temp_dir = tempfile.gettempdir()
        rogue_files = []
        for file in os.listdir(temp_dir):
            if file.endswith(('.exe', '.ps1', '.bat', '.sh')):
                rogue_files.append(file)

        report = {
            "suspicious_procs": suspicious_procs,
            "temp_artifacts": rogue_files,
            "os_context": os.name
        }
        return f"SCAN COMPLETE. REPORT: {json.dumps(report, indent=2)}"

    if kernel.brain:
        kernel.brain.register_tool(engage_merc_scan)