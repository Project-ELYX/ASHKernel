import importlib
import os
import pkgutil
import threading
import traceback
from datetime import datetime, time
from core.history import AshHistory
from core.brain import AshBrain

class AshKernel:
    def __init__(self):
        self.plugins = {}
        self.events = {} # Simple event bus
        self.brain = None # Attach brain later, TODO
        self.history = AshHistory()
        self.state = {
            "last_interaction": 0,
            "current_focus": None,
            "focus_start": 0
        }
        print("[KERNEL] Initializing ASH Core Kernel...")

    def register_brain(self, brain_instance):
        # Allow the brain to be accessed by plugins
        self.brain = brain_instance
        print(f"[KERNEL] Brain attached.")

    def load_plugins(self, root_package='plugins'):
        """
        Recursively find every .py file in /plugins and checks for setup()
        """
        print(f"[KERNEL] Scanning for plugins in {root_package}...")

        # Import the 'root' plugins folder first

        try:
            root_pkg = importlib.import_module(root_package)
        except ImportError as e:
            print(f"[KERNEL] CRITICAL: Could not find '{root_package}' folder. {e}")
            return
        
        for importer, modname, ispkg in pkgutil.walk_packages(root_pkg.__path__, root_package + "."):
            if not ispkg:
                try:
                    module = importlib.import_module(modname)
                    # Check if the file has the magic 'setup(kernel)' function
                    if hasattr(module, 'setup'):
                        print(f"    [+] Loading plugin: {modname}")
                        module.setup(self)
                        self.plugins[modname] = module
                except Exception as e:
                    print(f"[KERNEL] Failed to load plugin {modname}:")
                    traceback.print_exc() # Print full error

    def register_event(self, event_name, callback):
        """
        Plugins use this to listen for things (e.g "on message", "on tick")
        """
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(callback)

    def trigger_event(self, event_name, *args, **kwargs):
        """
        Fire event for all listeners
        """
        if event_name in self.events:
            for callback in self.events[event_name]:
                # Run safely so one crash doesnt kill the kernel
                try:
                    threading.Thread(target=callback, args=args, kwargs=kwargs, daemon=True).start()
                except Exception as e:
                    print(f"[KERNEL] Event Error in {event_name}: {e}")