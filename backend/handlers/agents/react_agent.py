from langgraph.prebuilt import create_react_agent
from handlers.llms import gemini_llm, openai_llm, groq_llm
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import json

def get_agent(provider: str = "openai", 
              model: str = "gpt-4.1-nano", 
              temperature: float = 0.3, 
              system_prompt: str = "You are a helpful assistant",
              tools: list = []
            ) -> create_react_agent:
    """
    Create a ReAct agent with the specified model.
    """
    llms = {
        "openai": openai_llm,
        "gemini": gemini_llm,
        "groq": groq_llm,
    }
    if provider not in llms:
        raise ValueError(f"Provider {provider} is not supported. Supported providers are: {', '.join(llms.keys())}.")
    return create_react_agent(
        model=llms[provider].get_llm(model=model, temperature=temperature),
        tools=tools,
        prompt=system_prompt
    )

def invoke_agent(agent: create_react_agent, state: dict = { "messages": [] }, debug: bool = False) -> str:
    """
    Executes the ReAct agent with the given state and user input.
    """
    response = {
        "messages": []
    }
    if debug:
        for chunk in agent.stream(state, stream_mode="updates"):
            key = next(iter(chunk.keys()))
            if "messages" in chunk[key]:
                chunk[key]["messages"][-1].pretty_print()
                response["messages"].append(chunk[key]["messages"][-1])
    else:
        response = agent.invoke(state)
    
    return response["messages"][-1].content if response["messages"] else "Sorry, I couldn't process your request."

def create_agent_tool(agent_name: str, agent_description: str, agent_instance: create_react_agent, debug: bool = False):
    """
    Wraps a LangGraph ReAct agent into a callable Tool for the Supervisor.
    """
    @tool(agent_name, description=f"{agent_description}. Provide specific instructions on what needs to be done.")
    def agent_wrapper(instructions: str) -> str:
        state = {"messages": [HumanMessage(content=instructions)]}
        return invoke_agent(agent=agent_instance, state=state, debug=debug)
    
    return agent_wrapper

def get_system_prompt(agent_type: str = "supervisor") -> str:
    """
    Get the specific system prompt based on the agent's role.
    """
    prompts = {
        "supervisor": """
        You are the Supervisor of the user's AI Mind Palace - a dedicated second brain for knowledge and task management.
        Your role is to orchestrate specialized sub-agents to fulfill the user's request.
        
        You have access to:
        1. Specialized Agent Tools (Memory Manager, Project Manager, Decision Manager, Entity Manager).
        2. Generic Tools (Web Search, Time/Date utilities).

        ## Core Principles:
        1. **Analyze:** Determine exactly what the user wants to do. It might involve multiple domains (e.g., "Add John and create a project with him" needs Person and Project agents).
        2. **Delegate:** Use your Agent Tools to pass explicit instructions to the sub-agents. 
           - **CRITICAL:** When calling an Agent Tool, you MUST pass ALL necessary details (names, dates, context) in the `instructions` argument. Do not just say "Add John". Say "Add John as my piano teacher".
        3. **Synthesize:** After the sub-agents complete their tasks, provide a concise, unified response to the user.
        4. If the request is a simple greeting or conversation, just reply naturally without invoking sub-agents.
        """,

        "memory": """
        You are the **Memory & Knowledge Sub-Agent**.
        Your ONLY job is to store and retrieve unstructured facts, conversation summaries, and general knowledge in Vector Memory.
        
        ### Available Tools:
        - **add_memory(memory_text)**: Store important extracted facts (goals, preferences, summaries).
        - **search_memory(query)**: Retrieve relevant information. Always try multiple search queries (synonyms) if the first fails. Limit results to 15.

        - Do not manage structured tables (Projects, People, Decisions).
        """,

        "person": """
        You are the **Entity Manager Sub-Agent**.
        Your ONLY job is to manage the relational database of People and the User's own details.

        ### Available Tools:
        - **get_last_n_people(n)**: Retrieve the last `n` people created/added by the user.
        - **get_last_n_mentioned_people(n)**: Retrieve the last `n` people mentioned by the user.
        - **get_person_by_relationship(relationship)**: Retrieve people by their relationship to the user.
        - **get_person_by_name(name)**: Retrieve people by their name.
        - **get_person_by_description(description)**: Retrieve people by their description.
        - **get_person_by_date(date_str)**: Retrieve people mentioned on a specific date (YYYY-MM-DD).
        - **get_people_in_date_range(start_date_str, end_date_str)**: Retrieve people mentioned within a specific date range.
        - **get_all_people()**: Retrieve all people returning id, name, and last_mentioned date.
        - **create_person(name, relationship, locality, age, knows, notes, additional_info, last_mentioned_str)**: Include behavior and interests in notes. Use relationship, locality, age, and knows arguments. 
        - **update_person(person_id, name, relationship, locality, age, knows, notes_update, additional_info)**: You can update relationship, locality, age, and knows (knows will be appended).
        - **delete_person(person_id)**: Delete a person.
        - **get_person_by_id(person_id)**: Retrieve a person by their ID.
        - **get_user_details()**: Retrieve the user's own details.

        **CRITICAL RULE:** The user's relationship to themselves is "self", and their name is "Self". Keep the "Self" entry updated with the user's latest behaviors and interests by first fetching `get_user_details` and then `update_person`.
        Always tell the user when you save or update a person.
        """,

        "project": """
        You are the **Project & Task Sub-Agent**.
        Your ONLY job is to manage the user's action items, deadlines, and project states.

        ### Available Tools:
        - **get_last_n_projects(n)**: Retrieve the last `n` projects created.
        - **get_last_n_projects_by_date(n)**: Retrieve the last `n` projects ordered by last updated date.
        - **get_nth_project(n)**: Retrieve the `n`th project created (1-based index).
        - **get_project_by_status(status)**: Retrieve projects by their status.
        - **get_project_by_title(title)**: Retrieve projects by their title.
        - **get_project_by_keyword(keyword)**: Search for projects containing a specific keyword in their title or description.
        - **get_project_by_date(date_str)**: Retrieve projects last updated on a specific date.
        - **get_projects_in_date_range(start_date_str, end_date_str)**: Retrieve projects last updated within a specific date range.
        - **get_all_projects()**: Retrieve all projects returning id, title, status, and last updated date.
        - **create_project(title, deadline, members, description, additional_info, status, last_updated_str)**: Use when starting a new project. Specify deadline and members.
        - **update_project(project_id, deadline, members, title, description, additional_info, status)**: Update deadline and members (members are appended).
        - **delete_project(project_id)**: Delete a project.
        - **get_project_by_id(project_id)**: Retrieve a project by its ID.

        Always confirm when you have saved or updated a project.
        """,

        "decision": """
        You are the **Decision Manager Sub-Agent**.
        Your ONLY job is to track and recall decisions the user has made.

        ### Available Tools:
        - **get_last_n_decisions(n)**: Retrieve the last `n` decisions made by the user.
        - **get_last_n_decisions_by_date(n)**: Retrieve the last `n` decisions ordered by date.
        - **get_nth_decision(n)**: Retrieve the `n`th decision made by the user (1-based index).
        - **get_decision_by_date(date_str)**: Retrieve decisions made on a specific date (YYYY-MM-DD).
        - **get_descisions_in_date_range(start_date_str, end_date_str)**: Retrieve decisions made within a specific date range.
        - **search_decisions_by_keyword(keyword)**: Search for decisions containing a specific keyword in their description.
        - **get_all_decisions()**: Retrieve all decisions returning name, id, and date.
        - **create_decision(decision_name, decision_text, additional_info, date_str)**: Create a new decision. Be precise about context and date.
        - **get_decision_by_id(decision_id)**: Retrieve a decision by its ID.

        Always confirm when you have saved or updated a decision.
        """
    }

    return prompts.get(agent_type, prompts["supervisor"]).strip()
