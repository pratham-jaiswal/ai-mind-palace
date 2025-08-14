from langchain_google_genai import ChatGoogleGenerativeAI
from llm_models import gemini_models

def get_llm(model: str = "gemini-2.0-flash-lite", temperature: float = 0.3) -> ChatGoogleGenerativeAI:
    if model not in gemini_models():
        raise ValueError(f"Model {model} is not supported.")
    llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    return llm
