from pathlib import Path
from utils.logger import get_logger
from utils.redis_client import get_redis

logger = get_logger(__name__)
redis_db = get_redis()

