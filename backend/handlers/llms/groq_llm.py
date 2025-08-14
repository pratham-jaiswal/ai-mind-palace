from langchain_groq import ChatGroq
from llm_models import groq_models

def get_llm(model: str = "openai/gpt-oss-20b", temperature: float = 0.3) -> ChatGroq:
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
