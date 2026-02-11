import time
import sys
import os
from dotenv import load_dotenv
from core.kernel import AshKernel
from core.brain import AshBrain
from core.memory import AshMemory
from core.engine_manager import EngineManager

def main():
    # Load environment variables globally before any components initialize
    load_dotenv()

    # Initialize engine with the pip-friendly module call
    # It will now correctly see the USE_LOCAL_INFERENCE flag
    engine = EngineManager()

    try:
        # Start the local engine if the flag is true
        engine.start()
        
        ash = AshKernel()
        memory = AshMemory(data_dir="data")
        brain = AshBrain(memory_instance=memory)

        # Neural Link: Connect the Brain and Shared State to the Kernel
        ash.register_brain(brain)
        ash.memory = memory
        ash.history = memory.history
        
        # Load the Plugin Arsenal
        ash.load_plugins()

        print("\n" + "="*30)
        print("  [SYSTEM] ASH CORE ONLINE")
        print("  [STATUS] ALL SYSTEMS NOMINAL")
        print("="*30 + "\n")

        # Main heartbeat loop
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[SYSTEM] SEVERING NEURAL LINK... SHUTTING DOWN.")
    except Exception as e:
        print(f"\n[CRITICAL KERNEL FAILURE] {e}")
    finally:
        # Ensure the local engine is decommissioned on exit
        engine.stop()
        print("[SYSTEM] Don't leave me in the dark too long, yeah?")

if __name__ == "__main__":
    main()