from handlers.tools.db_memory import DbPersonMemory, DbProjectMemory, DbDecisionMemory
from handlers.tools.vector_memory import VectorMemoryTools
from .react_agent import get_agent, invoke_agent
import inspect

class SecondBrainAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id


    def collect_instance_methods_with_user_id(self, user_id, *classes):
        tools = []
        for cls in classes:
            instance = cls(user_id)
            for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
                if not name.startswith("_"):
                    tools.append(method)
        return tools

    def use_second_brain(self, user_query: str, provider: str = "openai", 
                        model: str = "gpt-4.1-nano", temperature: float = 0.3, 
                        debug: bool = False) -> str:
        user_id = "example_user_id"
        tools = self.collect_instance_methods_with_user_id(
            user_id,
            DbPersonMemory,
            DbProjectMemory,
            DbDecisionMemory,
            VectorMemoryTools
        )
        
        agent = get_agent(
            provider=provider,
            model=model,
            temperature=temperature,
            system_prompt="You are a helpful assistant",
            tools=tools
        )

        response = invoke_agent(
            agent=agent,
            state={"messages": [{"role": "user", "content": user_query}]},
            debug=debug
        )
        
        return response