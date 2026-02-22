from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard(has_cart: bool = False) -> ReplyKeyboardMarkup:
    """
    Основное меню в зависимости от того, есть ли корзина у пользователя
    """
    kb = [
        [KeyboardButton(text="🛒 Каталог")],
    ]

    if has_cart:
        kb.append([KeyboardButton(text="🛍 Корзина")])
        kb.append([KeyboardButton(text="Продолжить покупки")])
    else:
        kb.append([KeyboardButton(text="Начать покупки")])

    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


def get_cart_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline-кнопки внутри корзины (пример)"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Очистить корзину", callback_data="cart_clear"),
            InlineKeyboardButton(text="Оформить заказ", callback_data="cart_checkout")
        ],
        [InlineKeyboardButton(text="Продолжить покупки", callback_data="back_to_catalog")]
    ])
    return kb
