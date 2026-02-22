from aiogram.fsm.state import State, StatesGroup

class ShopStates(StatesGroup):
    main_menu = State()
    viewing_catalog = State()
    viewing_product = State()      
    in_cart = State()               
    checkout = State()              