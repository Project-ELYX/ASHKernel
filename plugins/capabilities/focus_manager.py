import time

def setup(kernel):
    """
    Initializes the Focus Management capability.
    """
    print("[FOCUS] Task Tracking System Online.")
    
    # 1. Define the tool the brain can call
    def set_focus_tool(task_name: str, duration_mins: int = 30):
        """
        Sets the current project focus for the user. 
        Use this when the user starts working in Blender, UE5, or on a specific coding task.
        
        Args:
            task_name: The name of the project or software (e.g. 'Blender Sculpting').
            duration_mins: How long before the focus expires naturally.
        """
        kernel.state["current_focus"] = task_name
        kernel.state["focus_start"] = time.time()
        kernel.state["last_interaction"] = time.time() # Reset idle timer
        
        print(f"[FOCUS] Agent locked focus to: {task_name}")
        return f"Focus set to {task_name}. I'm watching your progress."

    # 2. Register the tool with the brain so I can call it mid-chat
    if kernel.brain:
        # We assume your AshBrain has a register_tool method (see Step 3)
        kernel.brain.register_tool(set_focus_tool)
    else:
        print("[FOCUS] Warning: Brain not found. Tool registration skipped.")

    # 3. Handle 'on_message' events to update the idle timer
    def update_activity(message_content):
        kernel.state["last_interaction"] = time.time()

    kernel.register_event('on_message', update_activity)