import os

DEV_ENV = os.getenv("DEV_ENV", "False").lower() in ("true", "1", "yes")
FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "./faiss_index")