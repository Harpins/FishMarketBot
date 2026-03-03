from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards import get_main_menu_keyboard
from states import ShopStates


router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    text = (
        "Добро пожаловать в Рыбный Магазин! 🐟✨\n"
        "Свежайшая рыба, морепродукты и икра ждут вас.\n\n"
    )

    await message.answer(text, reply_markup=get_main_menu_keyboard())

    await state.clear()
    await state.set_state(ShopStates.viewing_catalog)
