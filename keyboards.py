from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Основное меню
    """
    kb = [[KeyboardButton(text="🛒 Каталог")], [KeyboardButton(text="🛍 Корзина")]]

    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие...",
    )


def get_catalog_inline_keyboard(products: list) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком товаров (кнопки с названиями)
    products — список из Strapi (data)
    """
    kb = []
    for product in products:
        name = product.get("name", "Без названия")
        doc_id = product["documentId"]
        kb.append(
            [InlineKeyboardButton(text=name, callback_data=f"product_detail:{doc_id}")]
        )

    kb.append(
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back_to_menu")]
    )
    kb.append([InlineKeyboardButton(text="🛍 Корзина", callback_data="show_cart")])

    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_product_detail_keyboard(product_doc_id: str) -> InlineKeyboardMarkup:
    """
    Кнопки под карточкой товара
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Добавить в корзину",
                    callback_data=f"add_to_cart:{product_doc_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="← Назад к каталогу", callback_data="back_to_catalog"
                )
            ],
        ]
    )


def get_cart_keyboard(cart_items: list[dict]) -> InlineKeyboardMarkup:
    """
    Генератор кнопок корзины
    """
    rows = []

    if not cart_items:
        rows.append(
            [InlineKeyboardButton(text="← В меню", callback_data="back_to_menu")]
        )
    else:
        for item in cart_items:
            product = item.get("product", {})
            prod_name = product.get("name", "Товар без названия")
            qty = item.get("quantity", 0)
            prod_id = product.get("documentId", "")

            name_btn = InlineKeyboardButton(
                text=f"{prod_name} - {qty} шт.", callback_data="ignore"
            )
            minus_btn = InlineKeyboardButton(
                text="−", callback_data=f"remove_from_cart:{prod_id}"
            )
            plus_btn = InlineKeyboardButton(
                text="+", callback_data=f"add_to_cart:{prod_id}"
            )

            rows.append([name_btn, minus_btn, plus_btn])

        rows.append(
            [InlineKeyboardButton(text="← В меню", callback_data="back_to_menu")]
        )
        rows.append(
            [InlineKeyboardButton(text="← В каталог", callback_data="back_to_catalog")]
        )
        rows.append(
            [InlineKeyboardButton(text="Оплатить", callback_data="make_order")]
        )

    return InlineKeyboardMarkup(inline_keyboard=rows)
