from langchain_openai import ChatOpenAI
from llm_models import openai_models

def get_llm(model: str = "gpt-4.1-nano", temperature: float = 0.3) -> ChatOpenAI:
    if model not in openai_models():
        raise ValueError(f"Model {model} is not supported.")
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    return llm
