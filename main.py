import asyncio
from utils.logger import get_logger
from aiogram import Bot, Dispatcher
from config import TG_BOT_TOKEN

from handlers.cart import router as cart_router
from handlers.catalog import router as catalog_router
from handlers.start import router as start_router
from handlers.order import router as order_router

logger = get_logger(__name__)

async def main():

    bot = Bot(token=TG_BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_routers(cart_router, catalog_router, start_router, order_router)

    logger.critical("Tg-бот (магазин рыбы)  запущен")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical("(магазин рыбы) Критическая ошибка при tg-polling:", exc_info=True)
    finally:
        await bot.session.close()
        logger.critical("Tg-бот (магазин рыбы) остановлен")


if __name__ == "__main__":
    asyncio.run(main())