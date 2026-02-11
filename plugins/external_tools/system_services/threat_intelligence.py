import os
import requests
import subprocess
import hashlib
from dotenv import load_dotenv

load_dotenv()
VT_API_KEY = os.getenv("VT_API_KEY")

def setup(kernel):
    print("[MERC] Threat Intelligence Module Online.")

    # --- TOOL: VIRUSTOTAL FILE CHECK ---
    def check_file_reputation(file_path: str):
        """
        Hashes a file and checks its reputation against the VirusTotal database.
        """
        if not VT_API_KEY:
            return "ERROR: VT_API_KEY missing from .env."

        if not os.path.exists(file_path):
            return "ERROR: File path does not exist on the host."

        # Generate SHA-256 Hash
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()

        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        headers = {"x-api-key": VT_API_KEY}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                return f"No record found for hash {file_hash}. This file is either clean or brand new/unique (Ghost status)."
            
            data = response.json()
            stats = data['data']['attributes']['last_analysis_stats']
            return f"VT REPORT for {os.path.basename(file_path)}: {stats['malicious']} detections, {stats['suspicious']} suspicious flags. Status: {'THREAT' if stats['malicious'] > 0 else 'CLEAN'}."
        except Exception as e:
            return f"INTELLIGENCE FAILURE: {str(e)}"

    # --- TOOL: WEB RECONNAISSANCE ---
    def web_search_tool(query: str):
        """
        Performs a web search to identify unknown processes, IPs, or technical errors.
        """
        print(f"[MERC] Executing web recon for: {query}")
        # Using a simple DDG lite redirect for now
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        try:
            response = requests.get(url)
            data = response.json()
            abstract = data.get("AbstractText", "No direct abstract found.")
            return f"RECON DATA: {abstract if abstract else 'Search yielded no immediate definitions. Suggest manual deep dive.'}"
        except Exception as e:
            return f"RECON FAILURE: {str(e)}"

    if kernel.brain:
        kernel.brain.register_tool(check_file_reputation)
        kernel.brain.register_tool(web_search_tool)