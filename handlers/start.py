from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards import get_main_menu_keyboard
from utils.redis_ops import get_cart
from utils.api import get_customer_cart_status, sync_cart_on_checkout
from states import ShopStates
from utils.logger import get_logger

logger = get_logger(__name__)

router = Router(name="start")

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    platform = "telegram"

    has_cart, cart_info = await get_customer_cart_status(user_id)

    if not has_cart:
        redis_cart = get_cart(platform, user_id)
        has_cart = bool(redis_cart)

        if has_cart:
            success, result = await sync_cart_on_checkout(user_id, platform)
            if success:
                logger.info(f"Корзина из Redis успешно синхронизирована в Strapi для {user_id}")
                has_cart = True
            else:
                logger.warning(f"Не удалось синхронизировать Redis-корзину в Strapi: {result}")

    if has_cart:
        text = (
            "Рады видеть вас снова! 🐟✨\n"
            "Ваша корзина уже готова. Продолжим?"
        )
    else:
        text = (
            "Добро пожаловать в Рыбный Магазин! 🐟\n"
            "Свежайшая рыба и морепродукты ждут вас.\n\n"
            "Начнём покупки?"
        )

    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(has_cart=has_cart)
    )
    
    await state.clear()
    await state.set_state(ShopStates.viewing_catalog)