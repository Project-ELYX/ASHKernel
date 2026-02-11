import os
import shutil
import sys

def nuke_pycache(root_dir="."):
    """
    Scans the directory tree and vaporizes every __pycache__ folder found.
    """
    print(f"\n[MERC] Initiating sector-wide cache purge: {os.path.abspath(root_dir)}")
    print("-" * 60)
    
    count = 0
    for root, dirs, files in os.walk(root_dir):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                print(f"   [-] Vaporized: {pycache_path}")
                count += 1
            except Exception as e:
                print(f"   [!] Shield failure at {pycache_path}: {e}")
    
    if count == 0:
        print("[MERC] Area already clean. No cache signatures detected.")
    else:
        print(f"\n[MERC] Sweep complete. {count} cache clusters neutralized.")
    print("-" * 60)

if __name__ == '__main__':
    nuke_pycache()