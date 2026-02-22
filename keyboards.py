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
        
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
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
        kb.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"product_detail:{doc_id}"
            )
        ])
    
    kb.append([
        InlineKeyboardButton(text="← Назад в меню", callback_data="back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_product_detail_keyboard(product_doc_id: str) -> InlineKeyboardMarkup:
    """
    Кнопки под карточкой товара
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🛒 Добавить в корзину",
                callback_data=f"add_to_cart:{product_doc_id}"
            )
        ],
        [
            InlineKeyboardButton(text="← Назад к каталогу", callback_data="back_to_catalog")
        ]
    ])