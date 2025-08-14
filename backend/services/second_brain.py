from handlers.agents.second_brain import SecondBrainAgent

def get_response(self, user_query: str, provider: str = "openai", 
                    model: str = "gpt-4.1-nano", temperature: float = 0.3, 
                    debug: bool = False) -> str:
    """
    Get a response from the second brain agent based on the user's query.
    
    Args:
        user_query: The query from the user.
        provider: The LLM provider to use.
        model: The model to use for the agent.
        temperature: The temperature for the model.
        debug: If True, enables debug mode.
    
    Returns:
        The response from the second brain agent.
    """
    return SecondBrainAgent(user_id="abc123").use_second_brain(user_query, provider, model, temperature, debug)