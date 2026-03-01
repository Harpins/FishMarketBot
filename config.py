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

BASE_DIR = Path(__file__).parent
LANGUAGE_CODE = "ru-RU"