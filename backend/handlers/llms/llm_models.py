from utils.env_vars import DEV_ENV

def openai_models():
    return [
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-5-nano",
    ]

def gemini_models():
    return [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
    ]

def groq_models():
    if DEV_ENV: # Preview models for development. Read: https://console.groq.com/docs/models#preview-models
        return [
            "deepseek-r1-distill-llama-70b",
            "moonshotai/kimi-k2-instruct",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3-32b",
        ]
    return [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]
