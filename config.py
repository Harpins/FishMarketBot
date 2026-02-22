import environs
from pathlib import Path

env = environs.Env()
env.read_env()

TG_BOT_TOKEN = env.str("TG_BOT_TOKEN", "")
ERROR_BOT_TOKEN = env.str("ERROR_BOT_TOKEN", "")
ERROR_CHAT_ID = env.int("ERROR_CHAT_ID", None)
STRAPITOKEN = env.str("STRAPITOKEN", "")

STRAPIBASE = env.str("STRAPIBASE", "http://localhost:1337")
STRAPIURL = STRAPIBASE + "/api"

REDIS_SETTINGS = {
    "host": env.str("REDIS_HOST", "localhost"),
    "port": env.int("REDIS_PORT", 6379),
    "db": env.int("REDIS_DB", 0),
    "decode_responses": env.bool("REDIS_DECODE_RESPONSES", True),
}

BASE_DIR = Path(__file__).parent
LANGUAGE_CODE = "ru-RU"