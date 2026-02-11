import psutil
import socket
import json

def setup(kernel):
    print("[MERC] Network Mapping Module Online. Monitoring I/O traffic.")

    def map_network_tool():
        """
        Retrieves all active established network connections.
        Cross-platform (Linux/Windows) via psutil.
        """
        print("[MERC] Mapping network perimeter...")
        
        connections = []
        try:
            # kind='tcp' focuses on the standard established traffic
            for conn in psutil.net_connections(kind='tcp'):
                if conn.status == 'ESTABLISHED':
                    # Resolve process name from PID
                    try:
                        proc = psutil.Process(conn.pid)
                        proc_name = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_name = "Unknown/System"

                    connections.append({
                        "ProcessName": proc_name,
                        "PID": conn.pid,
                        "LocalAddr": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "RemoteIP": conn.raddr.ip if conn.raddr else "N/A",
                        "Port": conn.raddr.port if conn.raddr else "N/A"
                    })
            
            return json.dumps(connections, indent=2)
        except Exception as e:
            return f"MAP FAILED: {str(e)}"

    if kernel.brain:
        kernel.brain.register_tool(map_network_tool)