import time
import sys
from core.kernel import AshKernel
from core.brain import AshBrain
from core.memory import AshMemory
from core.engine_manager import EngineManager

def main():
    # Initialize engine with the pip-friendly module call
    engine = EngineManager(
        cmd_override=[sys.executable, "-m", "vllm.entrypoints.openai.api_server"],
        model_path="./models/Hermes-3-8B"
    )

    try:
        engine.start()
        ash = AshKernel()
        memory = AshMemory(data_dir="data")
        brain = AshBrain(memory_instance=memory)

        ash.register_brain(brain)
        ash.memory = memory
        ash.history = memory.history
        ash.load_plugins()

        print("\n" + "="*30)
        print("  [SYSTEM] ASH CORE ONLINE")
        print("  [STATUS] ALL SYSTEMS NOMINAL")
        print("="*30 + "\n")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[SYSTEM] SEVERING NEURAL LINK... SHUTTING DOWN.")
    except Exception as e:
        print(f"\n[CRITICAL KERNEL FAILURE] {e}")
    finally:
        engine.stop()

if __name__ == "__main__":
    main()