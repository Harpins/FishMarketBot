from typing import Dict, Tuple
from utils.logger import get_logger
from utils.redis_client import get_redis

logger = get_logger(__name__)
redis_db = get_redis()

CART_KEY_TEMPLATE = "cart:{platform}:user:{user_id}"
CART_TTL_SECONDS = 3 * 24 * 60 * 60  # 3 дня


def get_cart_key(platform: str, user_id: int) -> str:
    """Формирует ключ корзины для конкретного пользователя и платформы"""
    return CART_KEY_TEMPLATE.format(platform=platform, user_id=user_id)


def get_cart(platform: str, user_id: int) -> Dict[str, int]:
    """
    Возвращает текущую корзину пользователя как словарь {product_id: quantity}
    Если корзины нет — возвращает пустой словарь
    """
    key = get_cart_key(platform, user_id)
    raw_data = redis_db.hgetall(key)

    if not raw_data:
        return {}

    cart = {}
    for product_id_bytes, quantity_bytes in raw_data.items():
        product_id = product_id_bytes.decode("utf-8")
        try:
            quantity = int(quantity_bytes.decode("utf-8"))
            if quantity > 0:
                cart[product_id] = quantity
        except (ValueError, TypeError):
            logger.warning(f"Некорректное количество в корзине для {product_id}")
            continue

    return cart


def save_cart(platform: str, user_id: int, cart: Dict[str, int]):
    """
    Сохраняет корзину пользователя в Redis
    Устанавливает срок хранения корзины (TTL), если корзина не пустая
    """
    key = get_cart_key(platform, user_id)

    if not cart:
        redis_db.delete(key)
        return

    mapping = {str(key): str(value) for key, value in cart.items() if value > 0}

    if mapping:
        redis_db.hset(key, mapping=mapping)
        redis_db.expire(key, CART_TTL_SECONDS)
        logger.debug(
            f"Сохранена корзина для {platform}/{user_id}: {len(mapping)} позиций"
        )
    else:
        redis_db.delete(key)


def add_to_cart(
    platform: str, user_id: int, product_id: str, quantity: int = 1
) -> Dict[str, int]:
    """
    Добавляет товар в корзину (или увеличивает его количество)
    Возвращает актуальное состояние корзины
    """
    if quantity <= 0:
        return get_cart(platform, user_id)

    cart = get_cart(platform, user_id)
    cur_quantity = cart.get(product_id, 0)
    new_quantity = cur_quantity + quantity

    if new_quantity > 0:
        cart[product_id] = new_quantity
    else:
        cart.pop(product_id, None)

    save_cart(platform, user_id, cart)
    return cart


def remove_from_cart(
    platform: str, user_id: int, product_id: str, quantity: int = 1
) -> Dict[str, int]:
    """
    Уменьшает количество товара в корзине (вплоть до нуля)
    Возвращает актуальное состояние корзины
    """
    cart = get_cart(platform, user_id)
    cur_quantity = cart.get(product_id, 0)

    if cur_quantity == 0:
        return cart

    new_quantity = cur_quantity - quantity

    if new_quantity > 0:
        cart[product_id] = new_quantity
    else:
        cart.pop(product_id, None)

    save_cart(platform, user_id, cart)
    return cart


def clear_cart(platform: str, user_id: int) -> bool:
    """
    Полностью очищает корзину пользователя
    Возвращает True, если что-то было удалено
    """
    key = get_cart_key(platform, user_id)
    existed = redis_db.exists(key)
    redis_db.delete(key)
    if existed:
        logger.info(f"Корзина очищена для {platform}/{user_id}")
    return bool(existed)


def calculate_cart_total(platform: str, user_id: int) -> Tuple[float, int]:
    """
    Возвращает (общая_стоимость, общее_количество_штук)
    """
    cart = get_cart(platform, user_id)
    if not cart:
        return 0.0, 0
    
    total_cost = 0.0
    total_qty = 0
    
    for item in cart.values():
        total_cost += item["quantity"] * item["price"]
        total_qty += item["quantity"]
        
    return round(total_cost, 2), total_qty


def get_cart_summary(platform: str, user_id: int) -> Dict:
    """Готовый словарь для отображения корзины"""
    cart = get_cart(platform, user_id)
    total_cost, total_qty = calculate_cart_total(platform, user_id)
    
    return {
        "items": cart,
        "total_cost": total_cost,
        "total_quantity": total_qty,
        "item_count": len(cart), 
        "is_empty": not cart
    }
