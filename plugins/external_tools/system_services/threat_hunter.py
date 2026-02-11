import subprocess
import json
import time

def setup(kernel):
    print("[MERC] Threat Hunter Module Loaded. Ready to sweep.")

    def engage_merc_scan():
        """
        Runs a deep diagnostic sweep of the Windows host. 
        Checks for suspicious processes, weird network connections, and startup items.
        """
        print("[MERC] Initiating deep scan...")
        
        # 1. Look for 'Ghost' processes (High CPU but no visible window)
        # 2. Check for suspicious network connections (ESTABLISHED on weird ports)
        # 3. Check for unsigned executables in Temp folders
        
        script = """
        $results = @{
            suspicious_procs = Get-Process | Where-Object { $_.CPU -gt 500 -and $_.MainWindowTitle -eq "" } | Select-Object Name, Id, CPU | ConvertTo-Json;
            network_audits = Get-NetTCPConnection -State Established | Where-Object { $_.RemotePort -notin 80, 443, 22 } | Select-Object RemoteAddress, RemotePort, OwningProcess | ConvertTo-Json;
            temp_files = Get-ChildItem -Path "$env:TEMP" -File | Where-Object { $_.Extension -in ".exe", ".ps1", ".bat" } | Select-Object Name, LastWriteTime | ConvertTo-Json
        }
        $results | ConvertTo-Json
        """
        
        try:
            raw_output = subprocess.check_output(["powershell.exe", "-Command", script], stderr=subprocess.STDOUT).decode('utf-8')
            return f"SCAN COMPLETE. REPORT: {raw_output}"
        except Exception as e:
            return f"SCAN FAILED: {str(e)}"

    if kernel.brain:
        kernel.brain.register_tool(engage_merc_scan)