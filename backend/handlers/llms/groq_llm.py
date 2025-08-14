from langchain_groq import ChatGroq
from .llm_models import groq_models

def get_llm(model: str = "openai/gpt-oss-20b", temperature: float = 0.3) -> ChatGroq:
    """
    Get an Groq LLM instance.
    Args:
        model: The Groq model to use.
        temperature: The temperature for the model.
    Returns:
        An instance of ChatGroq configured with the specified model and temperature.
    Raises:
        ValueError: If the specified model is not supported.
    """
    if model not in groq_models():
        raise ValueError(f"Model {model} is not supported.")
    llm = ChatGroq(
        model=model,
        temperature=temperature,
        max_tokens=None,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
    )
    return llm
