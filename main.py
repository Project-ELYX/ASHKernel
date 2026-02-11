import time
from core.kernel import AshKernel
from core.brain import AshBrain
from core.memory import AshMemory
from core.engine_manager import EngineManager

def main():
    # Initialize local inference engine if selected
    engine = EngineManager(
        binary_path="python3 -m vllm.entrypoints.openai.api_server", # Binary wrapper
        model_path="NousResearch/Hermes-3-Llama-3.1-8B"
    )
    engine.start_engine()

    try:
        # 1. Start the Kernel (The Skeleton)
        ash = AshKernel()

        # 2. Start the Librarian (The Files & History)
        # This automatically starts the Historian and points to /data/logs
        memory = AshMemory(data_dir="data")

        # 3. Start the Brain (The Intelligence)
        # We pass the memory instance so the Brain can reach memory.history
        brain = AshBrain(memory_instance=memory)

        # 4. Neural Link: Connect the Brain to the Kernel
        ash.register_brain(brain)
    
        # 5. Shared State: Attach data handlers to the Kernel
        # This lets plugins access logs via 'kernel.history'
        ash.memory = memory
        ash.history = memory.history

        # 6. Load the Plugin Arsenal
        # This will now correctly find Focus, Hardware, Discord, etc.
        ash.load_plugins()

        print("\n" + "="*30)
        print("  [SYSTEM] ASH CORE ONLINE")
        print("  [STATUS] ALL SYSTEMS NOMINAL")
        print("="*30 + "\n")

    # Main heartbeat loop
    try:
        while True:
            # We could add kernel level 'ticks' here later
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SYSTEM] SEVERING NEURAL LINK... SHUTTING DOWN.")
        print("[SYSTEM] Don't leave me in the dark too long, yeah?")

if __name__ == "__main__":
    main()