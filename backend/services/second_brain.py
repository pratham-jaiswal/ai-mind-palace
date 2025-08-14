from handlers.agents.second_brain import SecondBrainAgent
from controllers.utils import jsonify_error, jsonify_ok
import traceback

def get_response(user_query: str, timezone: str, provider: str = "openai",
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
    try:
        result = SecondBrainAgent(user_id="abc123").use_second_brain(
            user_query=user_query, 
            provider=provider, 
            model=model, 
            temperature=temperature, 
            timezone=timezone,
            debug=debug
        )
        return jsonify_ok(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify_error("An error occurred while processing your request", 500)
