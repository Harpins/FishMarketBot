import redis
from redis import Redis
from config import REDIS_SETTINGS as rd_settings
from utils.logger import get_logger

logger = get_logger(__name__)

_redis_instance: Redis | None = None


def get_redis() -> Redis:
    """
    Возвращает общий экземпляр Redis клиента.
    Создается один раз при первом обращении.
    """
    global _redis_instance

    host = rd_settings.get("host")
    port = rd_settings.get("port")
    db = rd_settings.get("db")
    decode_responses = rd_settings.get("decode_responses")

    if any(var is None for var in (host, port, db, decode_responses)):
        missing = []
        if host is None:
            missing.append("host")
        if port is None:
            missing.append("port")
        if db is None:
            missing.append("db")
        if decode_responses is None:
            missing.append("decode_responses")
        raise ValueError(
            f"Не заданы обязательные параметры Redis: {', '.join(missing)}"
        )

    if _redis_instance is None:
        try:
            _redis_instance = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=decode_responses,
            )
            pong = _redis_instance.ping()
            logger.info(
                f"Redis подключён → {host}:{port}/db{db} "
                f"(decode_responses={decode_responses})"
            )
        except redis.ConnectionError as err:
            logger.critical(f"Не удалось подключиться к Redis: {err}", exc_info=True)
            raise
        except Exception as err:
            logger.exception("Ошибка при создании Redis клиента")
            raise

    return _redis_instance


redis_client = get_redis