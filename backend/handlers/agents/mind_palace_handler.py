from handlers.tools.db_memory import DbPersonMemory, DbProjectMemory, DbDecisionMemory
from handlers.tools.vector_memory import VectorMemoryTools
from handlers.tools.generic_tools import GenericTools
from .react_agent import get_agent, invoke_agent, get_system_prompt, create_agent_tool
from .conversation_handler import ConversationHandler
import inspect
from langchain_tavily import TavilySearch

class MindPalaceHandler:
    def __init__(self, user_id: str):
        self.user_id = user_id

    def collect_instance_methods(self, instance):
        tools = []
        for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
            if not name.startswith("_"):
                tools.append(method)
        return tools

    def use_mind_palace(self, user_query: str, timezone: str, thread_id: str, 
                         provider: str = "openai", model: str = "gpt-4.1-nano", 
                         temperature: float = 0.3, debug: bool = False) -> str:
        
        # Instantiate the tool classes
        person_db = DbPersonMemory(self.user_id)
        project_db = DbProjectMemory(self.user_id)
        decision_db = DbDecisionMemory(self.user_id)
        vector_db = VectorMemoryTools(self.user_id)
        generic = GenericTools(timezone)

        # Collect tools per domain
        person_tools = self.collect_instance_methods(person_db)
        project_tools = self.collect_instance_methods(project_db)
        decision_tools = self.collect_instance_methods(decision_db)
        memory_tools = self.collect_instance_methods(vector_db)
        
        generic_tools = self.collect_instance_methods(generic)
        generic_tools.append(TavilySearch(max_results=3))

        # Create domain-specific ReAct Sub-Agents
        person_agent = get_agent(provider, model, temperature, get_system_prompt("person"), person_tools)
        project_agent = get_agent(provider, model, temperature, get_system_prompt("project"), project_tools)
        decision_agent = get_agent(provider, model, temperature, get_system_prompt("decision"), decision_tools)
        memory_agent = get_agent(provider, model, temperature, get_system_prompt("memory"), memory_tools)

        # Wrap Sub-Agents into Tools for the Supervisor
        supervisor_tools = [
            create_agent_tool(
                "manage_people_and_entities", 
                "Use this to create, update, delete, search, or fetch details about people, relationships, or the user's own details ('Self').",
                person_agent, debug
            ),
            create_agent_tool(
                "manage_projects_and_tasks", 
                "Use this to create, update, delete, or fetch projects, tasks, action items, and deadlines.",
                project_agent, debug
            ),
            create_agent_tool(
                "manage_decisions", 
                "Use this to log, search, or retrieve decisions made by the user.",
                decision_agent, debug
            ),
            create_agent_tool(
                "manage_vector_memory", 
                "Use this to store, log, or search for unstructured facts, summaries, insights, or raw knowledge.",
                memory_agent, debug
            ),
        ] + generic_tools # Give the supervisor direct access to time and web lookup

        # Handle conversation history
        conversation_cls = ConversationHandler(self.user_id)
        if not thread_id.startswith(f"user-{self.user_id}--"):
            thread_id = f"user-{self.user_id}--{thread_id}"

        conversation_cls.create_conversation(thread_id=thread_id, message=user_query, sender="user")
        conversations = conversation_cls.get_conversations_by_thread_id(thread_id)

        state = {"messages": []}
        for conversation in conversations:
            state["messages"].append({"role": conversation.sender, "content": conversation.message})
        state["messages"].append({"role": "user", "content": user_query})
        
        # 5. Create Supervisor Agent
        supervisor_agent = get_agent(
            provider=provider,
            model=model,
            temperature=temperature,
            system_prompt=get_system_prompt("supervisor"),
            tools=supervisor_tools
        )

        response = invoke_agent(
            agent=supervisor_agent,
            state=state,
            debug=debug
        )

        conversation_cls.create_conversation(thread_id=thread_id, message=response, sender="ai")
        
        return {
            "response": response,
            "thread_id": thread_id
        }