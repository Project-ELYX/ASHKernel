import os
import json
from google import genai
from google.genai import types
from openai import OpenAI

class AshBrain:
    def __init__(self, memory_instance):
        self.memory_handler = memory_instance
        self.use_local = os.getenv("USE_LOCAL_INFERENCE", "false").lower() == "true"
        self.tools = [self.save_memory_tool, self.recall_recent_history]
        self.tool_map = {"save_memory_tool": self.save_memory_tool, "recall_recent_history": self.recall_recent_history}

        if self.use_local:
            self.client = OpenAI(api_key="local-token", base_url=os.getenv("LOCAL_API_BASE", "http://localhost:8000/v1"))
            self.model_id = os.getenv("LOCAL_MODEL_PATH", "./models/Hermes-3-8B")
        else:
            api_key = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY")
            self.client = genai.Client(api_key=api_key)
            self.model_id = 'gemini-1.5-flash'

    def register_tool(self, func):
        if func not in self.tools:
            self.tools.append(func)
            self.tool_map[func.__name__] = func

    def think(self, user_input, context=""):
        persona = self.memory_handler.load_persona()
        current_mem = self.memory_handler.get_memory()
        system_instr = f"{persona}\n\nMEMORY: {json.dumps(current_mem)}"

        if self.use_local:
            return self._local_think(user_input, context, system_instr)
        else:
            return self._cloud_think(user_input, context, system_instr)

    def _local_think(self, user_input, context, system_instr):
        """The Tool-Calling Loop for vLLM."""
        messages = [
            {"role": "system", "content": system_instr},
            {"role": "user", "content": f"CONTEXT: {context}\n\n{user_input}"}
        ]

        for _ in range(5):
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                tools=[{"type": "function", "function": {"name": n}} for n in self.tool_map.keys()]
            )
            
            msg = response.choices[0].message
            if not msg.tool_calls:
                return msg.content

            messages.append(msg)
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"[BRAIN] Local Tool Execution: {func_name}")
                result = self.tool_map[func_name](**args)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        return "ERROR: Local tool loop timed out."

    def _cloud_think(self, user_input, context, system_instr):
        # Simplified config to avoid validation errors with the latest SDK
        config = types.GenerateContentConfig(
            system_instruction=system_instr,
            tools=self.tools
        )
        resp = self.client.models.generate_content(
            model=self.model_id,
            contents=f"CONTEXT: {context}\n\n{user_input}",
            config=config
        )
        return resp.text

    def save_memory_tool(self, category: str, fact: str):
        self.memory_handler.update_memory(category, fact)
        return f"Fact committed to {category}."

    def recall_recent_history(self, count: int = 15):
        return self.memory_handler.history.get_recent(count)