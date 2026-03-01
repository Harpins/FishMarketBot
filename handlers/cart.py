from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.api import (
    get_or_create_cart,
    add_to_cart,
    remove_from_cart,
)

from keyboards import get_cart_keyboard
from states import ShopStates

from utils.logger import get_logger

logger = get_logger(__name__)

router = Router(name="cart")


@router.message(F.text.lower().contains("корзина"))
@router.callback_query(F.data == "show_cart")
async def show_cart_handler(event: Message | CallbackQuery, state: FSMContext):
    user_id = event.from_user.id if isinstance(event, Message) else event.from_user.id
    is_callback = isinstance(event, CallbackQuery)

    cart = await get_or_create_cart(user_id)
    if not cart:
        text = "Не удалось загрузить корзину 😔 Попробуйте позже."
        if is_callback:
            await event.answer(text, show_alert=True)
        else:
            await event.answer(text)
        return

    items = cart.get("cartproducts", [])

    if not items:
        text = "Ваша корзина пуста 🛒\nДобавьте товары из каталога!"
    else:
        lines = []
        total_qty = 0
        total_mass = 0.00
        total_price = 0.00
        for item in items:
            prod = item.get("product", {})
            name = prod.get("name", "Без названия")
            mass = prod.get("mass_g", 0.00)
            mass_txt = f"{mass} г" if mass != 0 else ""
            price = prod.get("price", 0.00)
            qty = item.get("quantity", 0)
            total_mass += mass * qty
            pos_price = price * qty
            total_qty += qty
            total_price += pos_price
            lines.append(
                f"• {name} ({mass_txt}) в количестве {qty} шт. - {pos_price} руб."
            )
        text = (
            "Ваша корзина:\n\n"
            + "\n".join(lines)
            + f"\n\n Всего: {total_qty} товаров на сумму {total_price} руб."
            + f"\n Масса заказа {round(total_mass / 1000, 2)} кг"
        )

    keyboard = get_cart_keyboard(items)

    if is_callback:
        await update_cart_message(event.message, text, keyboard)
        await event.answer()
    else:
        await event.answer(text, reply_markup=keyboard)
        await state.set_state(ShopStates.in_cart)


async def update_cart_message(message: Message, text: str, keyboard):
    if message.text:
        try:
            await message.edit_text(text=text, reply_markup=keyboard, parse_mode="HTML")
            return True
        except Exception as e:
            logger.warning(f"Не удалось отредактировать сообщение корзины: {e}")
    try:
        await message.delete()
    except Exception as e:
        logger.debug(f"Не удалось удалить старое сообщение: {e}")

    await message.answer(text, reply_markup=keyboard)
    return True


@router.callback_query(F.data.startswith("add_to_cart:"))
async def process_add_to_cart(callback: CallbackQuery, state: FSMContext):
    _, product_id = callback.data.split(":", 1)
    user_id = callback.from_user.id

    success = await add_to_cart(user_id, product_id)

    if success:
        await callback.answer("1 товар добавлен", show_alert=False)
        await show_cart_handler(callback, state)
    else:
        await callback.answer("Не удалось добавить", show_alert=True)


@router.callback_query(F.data.startswith("remove_from_cart:"))
async def process_remove_from_cart(callback: CallbackQuery, state: FSMContext):
    _, product_id = callback.data.split(":", 1)
    user_id = callback.from_user.id

    success = await remove_from_cart(user_id, product_id)

    if success:
        await callback.answer("1 товар убран", show_alert=False)
        await show_cart_handler(callback, state)
    else:
        await callback.answer("Не удалось убрать", show_alert=True)
