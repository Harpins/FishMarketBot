from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🛒 Каталог рыбы")],
        [KeyboardButton(text="🛍 Корзина")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие...",
    )


def product_card(product_id: int, in_cart: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ В корзину", callback_data=f"add_to_cart:{product_id}")
    if in_cart:
        builder.button(
            text="🗑 Убрать из корзины", callback_data=f"remove_from_cart:{product_id}"
        )
    builder.adjust(1)
    return builder.as_markup()


def cart_actions(cart_items_count: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if cart_items_count > 0:
        builder.button(text="Очистить корзину", callback_data="clear_cart")
        builder.button(text="Оформить заказ", callback_data="checkout")
    builder.button(text="← Назад в каталог", callback_data="back_to_catalog")
    builder.adjust(1)
    return builder.as_markup()


def product_pagination(page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if page > 0:
        builder.button(text="⬅ Предыдущая", callback_data=f"catalog_page:{page-1}")
    if page < total_pages - 1:
        builder.button(text="Следующая ➡", callback_data=f"catalog_page:{page+1}")
    builder.button(text="← В меню", callback_data="back_to_menu")
    builder.adjust(2)
    return builder.as_markup()
