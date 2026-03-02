from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import re
from states import ShopStates

from utils.api import update_customer_email

from utils.logger import get_logger

logger = get_logger(__name__)

router = Router(name="order")


@router.callback_query(F.data == "make_order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Для оформления заказа укажите ваш email:", reply_markup=None
    )
    await state.set_state(ShopStates.entering_email)
    await callback.answer()
    

@router.message(ShopStates.entering_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await message.answer("Пожалуйста, введите корректный email (пример: name@example.com)")
        return

    user_id = message.from_user.id

    success = await update_customer_email(user_id, email)

    if success:
        await message.answer(
            "Заказ оформлен! 🎉\nМы свяжемся с вами в ближайшее время.\nСпасибо за покупку!",
            reply_markup=None 
        )
    else:
        await message.answer(
            "Не удалось сохранить email 😔\nПопробуйте позже или свяжитесь с поддержкой."
        )
    await state.clear()
