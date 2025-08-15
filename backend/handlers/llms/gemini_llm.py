from langchain_google_genai import ChatGoogleGenerativeAI
from .llm_models import gemini_models

def get_llm(model: str = "gemini-2.0-flash-lite", temperature: float = 0.3) -> ChatGoogleGenerativeAI:
    """
    Get an Gemini LLM instance.
    Args:
        model: The Gemini model to use.
        temperature: The temperature for the model.
    Returns:
        An instance of ChatGoogleGenerativeAI configured with the specified model and temperature.
    Raises:
        ValueError: If the specified model is not supported.
    """
    
    if model not in gemini_models():
        raise ValueError(f"Model {model} is not supported.")
    llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=25,
    )
    return llm
