import aiohttp
from datetime import datetime
from config import STRAPIBASE, STRAPIURL, STRAPITOKEN
from utils.redis_ops import get_cart
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_products(page: int = 1, page_size: int = 10):
    """Получаем товары с пагинацией"""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {STRAPITOKEN}"}
        params = {
            "pagination[page]": page,
            "pagination[pageSize]": page_size,
            "sort": "name:asc",
        }
        async with session.get(
            f"{STRAPIURL}/products", headers=headers, params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"], data["meta"]["pagination"]
            return [], {}


async def get_product(product_id: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {STRAPITOKEN}",
            "Accept": "application/json",
        }
        params = {"populate": "image"}
        async with session.get(
            f"{STRAPIURL}/products/{product_id}", headers=headers, params=params
        ) as response:
            if response.status == 200:
                json_data = await response.json()
                product = json_data.get("data")
                if not product:
                    return None
                if product.get("image"):
                    img = product["image"]
                    if img.get("url"):
                        product["image_full_url"] = STRAPIBASE + img["url"]
                return product
            return None


async def sync_cart_on_checkout(user_id: int, platform: str = "telegram"):
    """
    Вызывается при нажатии кнопки «Оформить заказ»:
    1. Находит или создает customer по tg_id
    2. Создает или обновляет cart
    3. Удаляет старые cartproduct и создает новые на основе Redis-корзины
    """
    cart = get_cart(platform, user_id)
    if not cart:
        return False, "Корзина пуста"

    headers = {
        "Authorization": f"Bearer {STRAPITOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        customer = await _ensure_customer(session, headers, user_id)
        if not customer:
            return False, "Не удалось получить/создать customer"

        customer_doc_id = customer["documentId"]

        cart_entry = await _ensure_cart(session, headers, customer_doc_id)
        if not cart_entry:
            return False, "Не удалось создать/обновить cart"

        cart_doc_id = cart_entry["documentId"]

        success = await _replace_cart_products(session, headers, cart_doc_id, cart)
        if not success:
            return False, "Ошибка при записи позиций корзины"

        return True, {
            "cart_documentId": cart_doc_id,
            "customer_documentId": customer_doc_id,
            "positions": len(cart),
        }


async def _ensure_customer(session: aiohttp.ClientSession, headers: dict, tg_id: int):
    url = f"{STRAPIURL}/customers"
    params = {"filters[tg_id][$eq]": str(tg_id), "pagination[limit]": 1}

    async with session.get(url, headers=headers, params=params) as r:
        if r.status == 200:
            data = await r.json()
            if data.get("data"):
                return data["data"][0]

    payload = {"data": {"tg_id": str(tg_id), "email": None}}
    async with session.post(url, json=payload, headers=headers) as r:
        if r.status in (200, 201):
            return (await r.json())["data"]
        logger.error(f"Ошибка создания customer: {r.status} {await r.text()}")
        return None


async def _ensure_cart(
    session: aiohttp.ClientSession, headers: dict, customer_doc_id: str
):
    url = f"{STRAPIURL}/carts"
    params = {"filters[user][documentId][$eq]": customer_doc_id, "pagination[limit]": 1}

    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            data = await response.json()
            if data.get("data"):
                cart = data["data"][0]
                up_payload = {"data": {"last_updated": datetime.now().isoformat()}}
                up_url = f"{url}/{cart['documentId']}"
                async with session.put(up_url, json=up_payload, headers=headers) as ur:
                    if ur.status not in (200, 201):
                        logger.warning(
                            f"Не удалось обновить timestamp cart: {ur.status}"
                        )
                return cart

    payload = {"data": {"user": customer_doc_id, "status": "pending_order"}}
    async with session.post(url, json=payload, headers=headers) as response:
        if response.status in (200, 201):
            return (await response.json())["data"]
        logger.error(f"Ошибка создания cart: {response.status} {await response.text()}")
        return None


async def _replace_cart_products(
    session: aiohttp.ClientSession, headers: dict, cart_doc_id: str, cart
) -> bool:
    base = f"{STRAPIURL}/cartproducts"

    search_params = {"filters[cart][documentId][$eq]": cart_doc_id}
    async with session.get(base, headers=headers, params=search_params) as response:
        if response.status == 200:
            old_items = (await response.json()).get("data", [])
            for old in old_items:
                del_url = f"{base}/{old['documentId']}"
                async with session.delete(del_url, headers=headers) as dr:
                    if dr.status not in (200, 204):
                        logger.warning(
                            f"Не удалось удалить старый cartproduct {old['documentId']}"
                        )

    success = True
    for product_doc_id, quantity in cart.items():
        payload = {
            "data": {
                "cart": cart_doc_id,
                "product": product_doc_id,
                "quantity": float(quantity),
            }
        }
        async with session.post(base, json=payload, headers=headers) as response:
            if response.status not in (200, 201):
                logger.error(
                    f"Не удалось создать cartproduct для {product_doc_id}: {response.status} {await response.text()}"
                )
                success = False

    return success
