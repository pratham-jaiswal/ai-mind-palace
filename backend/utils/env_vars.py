import os

DEV_ENV = os.getenv("DEV_ENV", "False").lower() in ("true", "1", "yes")