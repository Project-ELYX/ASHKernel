import subprocess
import json
import time

def setup(kernel):
    print("[MERC] Network Mapping Module Online. Monitoring I/O traffic.")

    def map_network_tool():
        """
        Retrieves all active established network connections on the Windows host.
        Links IP addresses and ports to the specific Process Name and ID.
        """
        print("[MERC] Mapping network perimeter...")
        
        # PowerShell script to get established connections and join them with process names
        script = """
        $connections = Get-NetTCPConnection -State Established | Select-Object RemoteAddress, RemotePort, OwningProcess;
        $report = foreach ($c in $connections) {
            $p = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue;
            [PSCustomObject]@{
                ProcessName = if ($p) { $p.Name } else { "Unknown" };
                PID         = $c.OwningProcess;
                RemoteIP    = $c.RemoteAddress;
                Port        = $c.RemotePort
            }
        };
        $report | ConvertTo-Json
        """
        
        try:
            output = subprocess.check_output(["powershell.exe", "-Command", script], stderr=subprocess.STDOUT).decode('utf-8')
            return f"NETWORK MAP DATA: {output}"
        except Exception as e:
            return f"MAP FAILED: {str(e)}"

    if kernel.brain:
        kernel.brain.register_tool(map_network_tool)