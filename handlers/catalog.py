from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    BufferedInputFile,
    InputMediaPhoto,
    ReplyKeyboardRemove,
)
from aiogram.fsm.context import FSMContext
import aiohttp
from handlers.start import cmd_start
from utils.api import get_products, get_product
from keyboards import (
    get_catalog_inline_keyboard,
    get_product_detail_keyboard,
)
from states import ShopStates

from utils.logger import get_logger

logger = get_logger(__name__)

router = Router(name="catalog")


@router.message(F.text.lower().contains("каталог"))
async def show_catalog(message: Message, state: FSMContext):
    """Показывает список товаров при нажатии на кнопку Каталог"""
    products, pagination = await get_products(page=1, page_size=15)

    if not products:
        await message.answer("Каталог пуст 😔 Проверьте позже.")
        return

    text = "Выберите товар из каталога:\n"

    await message.answer(text="Готовим каталог", reply_markup=ReplyKeyboardRemove())
    await message.answer(text, reply_markup=get_catalog_inline_keyboard(products))

    await state.set_state(ShopStates.viewing_catalog)


@router.callback_query(F.data.startswith("product_detail:"))
async def show_product_detail(callback: CallbackQuery, state: FSMContext):
    """Открывает подробную карточку товара"""
    _, product_id = callback.data.split(":", 1)

    product = await get_product(product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    name = product.get("name", "без названия")
    price = product.get("price", "по запросу")
    mass_g = product.get("mass_g", 1000)
    description = product.get("description", "описание отсутствует")
    image_url = product.get("image_full_url")

    text = f"🐟 {name}\n\n💰 {price} ₽ за {mass_g} г\n\n{description}"

    if image_url:
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=image_url, caption=text, parse_mode="HTML"),
                reply_markup=get_product_detail_keyboard(product_id),
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить картинку по URL {image_url}: {e}")
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            image_bytes = await resp.read()
                            await callback.message.edit_media(
                                media=InputMediaPhoto(
                                    media=BufferedInputFile(
                                        file=image_bytes,
                                        filename=f"product_{product_id}.jpg",
                                    ),
                                    caption=text,
                                    parse_mode="HTML",
                                ),
                                reply_markup=get_product_detail_keyboard(product_id),
                            )
                        else:
                            raise Exception("Не удалось скачать изображение")
            except Exception as download_error:
                logger.error(f"Ошибка скачивания: {download_error}")
                await callback.message.edit_text(
                    text=text + "\n\n(фото недоступно)",
                    parse_mode="HTML",
                    reply_markup=get_product_detail_keyboard(product_id),
                )
    else:
        await callback.message.answer(
            text, reply_markup=get_product_detail_keyboard(product_id)
        )

    await callback.answer()
    await state.set_state(ShopStates.viewing_product)


@router.callback_query(F.data == "back_to_catalog")
async def back_to_catalog(callback: CallbackQuery, state: FSMContext):
    """Возврат к списку товаров"""
    try:
        await callback.message.delete()
    except Exception:
        pass

    await show_catalog(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()

    try:
        await callback.message.delete()
    except Exception:
        pass

    await cmd_start(callback.message, state)
    await callback.answer()
