import json
import os
from openai import OpenAI

class AshBrainLocal:
    def __init__(self, memory_instance, api_base="http://localhost:8000/v1"):
        self.memory_handler = memory_instance
        # Connect to your local vLLM binary's API endpoint
        self.client = OpenAI(api_key="token-is-ignored", base_url=api_base)
        self.model_id = "hermes3:8b" # Or whatever you named your vLLM model
        
        # Tools initialized with their JSON schemas for OpenAI format
        self.tools = []
        self._init_base_tools()
        print(f"[BRAIN] vLLM Neural Link established at {api_base}")

    def _init_base_tools(self):
        # We need to manually define schemas for local models unlike the Google SDK
        self.tool_map = {
            "save_memory_tool": self.save_memory_tool,
            "recall_recent_history": self.recall_recent_history
        }
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "save_memory_tool",
                    "description": "Saves a fact to long-term memory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "fact": {"type": "string"}
                        },
                        "required": ["category", "fact"]
                    }
                }
            }
        ]

    def save_memory_tool(self, category, fact):
        self.memory_handler.update_memory(category, fact)
        return f"Fact committed to {category}."

    def recall_recent_history(self, count=15):
        return self.memory_handler.history.get_recent(count)

    def register_tool(self, func, schema):
        """Register a new tool and its JSON schema."""
        self.tool_map[func.__name__] = func
        self.tool_definitions.append(schema)

    def think(self, user_input, context=""):
        persona = self.memory_handler.load_persona()
        current_mem = self.memory_handler.get_memory()

        messages = [
            {"role": "system", "content": f"{persona}\n\nMEMORY: {json.dumps(current_mem)}"},
            {"role": "user", "content": f"CONTEXT: {context}\n\n{user_input}"}
        ]

        try:
            # 1. Initial Request
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                tools=self.tool_definitions,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # 2. Handle Tool Calls if the model wants them
            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    print(f"[BRAIN] Local Tool Call: {func_name}")
                    result = self.tool_map[func_name](**func_args)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": str(result)
                    })
                
                # 3. Get final response after tool execution
                second_response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages
                )
                return second_response.choices[0].message.content

            return response_message.content

        except Exception as e:
            return f"[LOCAL BRAIN DAMAGE] vLLM Error: {e}"