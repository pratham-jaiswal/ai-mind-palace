from handlers.tools.db_memory import DbPersonMemory, DbProjectMemory, DbDecisionMemory
from handlers.tools.vector_memory import VectorMemoryTools
from handlers.tools.generic_tools import GenericTools
from .react_agent import get_agent, invoke_agent, get_system_prompt
from .conversation_handler import ConversationHandler
import inspect

class MindPalaceHandler:
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
    
    def collect_generic_tools(self, timezone, *classes):
        tools = []
        for cls in classes:
            instance = cls(timezone)
            for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
                if not name.startswith("_"):
                    tools.append(method)
        return tools

    def use_mind_palace(self, user_query: str, timezone: str, thread_id: str, 
                         provider: str = "openai", model: str = "gpt-4.1-nano", 
                         temperature: float = 0.3, debug: bool = False) -> str:
        tools = self.collect_instance_methods_with_user_id(
            self.user_id,
            DbPersonMemory,
            DbProjectMemory,
            DbDecisionMemory,
            VectorMemoryTools
        ) + self.collect_generic_tools(
            timezone,
            GenericTools
        )

        conversation_cls = ConversationHandler(self.user_id)
        
        if not thread_id.startswith(f"user-{self.user_id}--"):
            thread_id = f"user-{self.user_id}--{thread_id}"

        conversation_cls.create_conversation(
            thread_id=thread_id,
            message=user_query,
            sender="user"
        )

        conversations = conversation_cls.get_conversations_by_thread_id(thread_id)

        state = {
            "messages": []
        }
        for conversation in conversations:
            state["messages"].append({"role": conversation.sender, "content": conversation.message})
        state["messages"].append({"role": "user", "content": user_query})
        
        agent = get_agent(
            provider=provider,
            model=model,
            temperature=temperature,
            system_prompt=get_system_prompt(),
            tools=tools
        )

        response = invoke_agent(
            agent=agent,
            state=state,
            debug=debug
        )

        conversation_cls.create_conversation(
            thread_id=thread_id,
            message=response,
            sender="ai"
        )
        
        return {
            "response": response,
            "thread_id": thread_id
        }