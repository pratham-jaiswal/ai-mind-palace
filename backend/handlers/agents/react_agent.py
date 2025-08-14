from langgraph.prebuilt import create_react_agent
from llms import gemini_llm, openai_llm, groq_llm

def get_agent(provider: str = "openai", 
              model: str = "gpt-4.1-nano", 
              temperature: float = 0.3, 
              system_prompt: str = "You are a helpful assistant",
              tools: list = []
            ) -> create_react_agent:
    """
    Create a ReAct agent with the specified model.
    
    Args:
        provider: The LLM provider to use (e.g., "openai", "gemini", "groq").
        model: The model to use for the agent.
        temperature: The temperature for the model.
        system_prompt: The system prompt to initialize the agent.
        tools: A list of tools that the agent can use.
        
    Returns:
        An instance of a React agent.
    
    Raises:
        ValueError: If the specified provider is not supported.
    """
    llms = {
        "openai": openai_llm.get_llm(model=model, temperature=temperature),
        "gemini": gemini_llm.get_llm(model=model, temperature=temperature),
        "groq": groq_llm.get_llm(model=model, temperature=temperature),
    }
    if provider not in llms:
        raise ValueError(f"Provider {provider} is not supported. Supported providers are: {', '.join(llms.keys())}.")
    return create_react_agent(
        model=llms[provider],
        tools=tools,
        prompt=system_prompt
    )

def invoke_agent(agent: create_react_agent, state: dict = { "messages": [] }, debug: bool = False) -> str:
    """
    Executes the ReAct agent with the given state and user input.
    
    Args:
        agent: The ReAct agent instance to be invoked.
        state: A dictionary representing the current conversation state.
        debug: If True, streams and prints debug information during execution.
        
    Returns:
        The content of the agent's final response message, or a fallback message if no response is available.
    """
    response = {
        "message": []
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
