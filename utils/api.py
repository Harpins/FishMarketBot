import aiohttp
from config import STRAPIBASE, STRAPIURL, STRAPITOKEN
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
                logger.info(f"Найдено {len(data["data"])} продуктов")
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
                response_data = await response.json()
                product = response_data.get("data")
                if not product:
                    return None
                if product.get("image"):
                    img = product["image"]
                    if img.get("url"):
                        product["image_full_url"] = STRAPIBASE + img["url"]
                return product
            return None


async def get_or_create_customer(tg_id: int):
    """
    Находит пользователя по tg_id или создаёт нового.
    Возвращает данные пользователя (включая documentId) или None при ошибке.
    """
    headers = {
        "Authorization": f"Bearer {STRAPITOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        search_params = {"filters[tg_id][$eq]": str(tg_id), "pagination[limit]": 1}
        async with session.get(
            f"{STRAPIURL}/customers", headers=headers, params=search_params
        ) as response:
            if response.status == 200:
                response_data = await response.json()
                if response_data.get("data"):
                    return response_data["data"][0]

        payload = {"data": {"tg_id": str(tg_id)}}
        async with session.post(
            f"{STRAPIURL}/customers", json=payload, headers=headers
        ) as response:
            if response.status in (200, 201):
                return (await response.json())["data"]
            else:
                text = await response.text()
                logger.error(
                    f"Ошибка создания customer tg_{tg_id}: {response.status} {text}"
                )
                return None


async def get_or_create_cart(tg_id: int):
    customer = await get_or_create_customer(tg_id)
    if not customer:
        return None

    customer_id = customer["documentId"]
    headers = {
        "Authorization": f"Bearer {STRAPITOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        params = {
            "filters[customer][documentId][$eq]": customer_id,
            "pagination[limit]": 1,
            "populate": "cartproducts.product",
        }
        async with session.get(
            f"{STRAPIURL}/carts", headers=headers, params=params
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("data"):
                    return data["data"][0]

        payload = {
            "data": {
                "customer": customer_id,
            }
        }
        async with session.post(
            f"{STRAPIURL}/carts", json=payload, headers=headers
        ) as resp:
            if resp.status in (200, 201):
                logger.info(f"Создана корзина для tg_{tg_id}")
                return (await resp.json())["data"]
            else:
                error = await resp.text()
                logger.error(f"Ошибка создания корзины: {resp.status} {error}")
                return None


async def add_to_cart(tg_id: int, product_doc_id: str):
    """
    Добавляет ровно 1 единицу товара в корзину.
    Если товар уже есть - увеличивает количество на 1.
    """
    cart = await get_or_create_cart(tg_id)
    if not cart:
        logger.error(f"Не удалось получить/создать корзину для tg_{tg_id}")
        return False

    cart_doc_id = cart["documentId"]
    headers = {
        "Authorization": f"Bearer {STRAPITOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        params = {
            "filters[cart][documentId][$eq]": cart_doc_id,
            "filters[product][documentId][$eq]": product_doc_id,
            "pagination[limit]": 1,
        }

        async with session.get(
            f"{STRAPIURL}/cartproducts", headers=headers, params=params
        ) as resp:
            if resp.status != 200:
                logger.error(f"Ошибка поиска позиции: {resp.status}")
                return False

            data = await resp.json()
            if data.get("data"):
                item = data["data"][0]
                new_qty = item["quantity"] + 1

                payload = {"data": {"quantity": new_qty}}
                upd_url = f"{STRAPIURL}/cartproducts/{item['documentId']}"
                async with session.put(upd_url, json=payload, headers=headers) as ur:
                    if ur.status not in (200, 201):
                        logger.error(f"Не удалось увеличить количество: {ur.status}")
                        return False
            else:
                payload = {
                    "data": {
                        "cart": cart_doc_id,
                        "product": product_doc_id,
                        "quantity": 1,
                    }
                }
                async with session.post(
                    f"{STRAPIURL}/cartproducts", json=payload, headers=headers
                ) as cr:
                    if cr.status not in (200, 201):
                        logger.error(
                            f"Ошибка создания позиции: {cr.status} {await cr.text()}"
                        )
                        return False

    logger.info(f"Добавлен товар {product_doc_id} в количестве 1 шт. для tg_{tg_id}")
    return True


async def remove_from_cart(tg_id: int, product_doc_id: str):
    """
    Уменьшает количество товара в корзине на 1.
    Если количество становится ≤ 0 - удаляет позицию полностью.
    Если товара нет в корзине - ничего не делает и возвращает True.
    """

    cart = await get_or_create_cart(tg_id)
    if not cart:
        logger.error(f"Не удалось получить корзину для tg_{tg_id}")
        return False

    cart_doc_id = cart["documentId"]
    headers = {
        "Authorization": f"Bearer {STRAPITOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        params = {
            "filters[cart][documentId][$eq]": cart_doc_id,
            "filters[product][documentId][$eq]": product_doc_id,
            "pagination[limit]": 1,
        }

        async with session.get(
            f"{STRAPIURL}/cartproducts", headers=headers, params=params
        ) as resp:
            if resp.status != 200:
                logger.error(f"Ошибка поиска позиции для удаления: {resp.status}")
                return False

            data = await resp.json()
            if not data.get("data"):
                return True

            item = data["data"][0]
            current_qty = item["quantity"]
            new_qty = current_qty - 1

            if new_qty <= 0:
                del_url = f"{STRAPIURL}/cartproducts/{item['documentId']}"
                async with session.delete(del_url, headers=headers) as dr:
                    if dr.status not in (200, 204):
                        logger.error(
                            f"Не удалось удалить позицию {item['documentId']}: {dr.status}"
                        )
                        return False
            else:
                payload = {"data": {"quantity": new_qty}}
                upd_url = f"{STRAPIURL}/cartproducts/{item['documentId']}"
                async with session.put(upd_url, json=payload, headers=headers) as ur:
                    if ur.status not in (200, 201):
                        logger.error(
                            f"Не удалось уменьшить количество: {ur.status} {await ur.text()}"
                        )
                        return False

    logger.info(f"Количество товара {product_doc_id} уменьшено на 1 шт. для tg_{tg_id}")
    return True


async def update_customer_email(tg_id: int, email: str) -> bool:
    headers = {
        "Authorization": f"Bearer {STRAPITOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        params = {"filters[tg_id][$eq]": str(tg_id), "pagination[limit]": 1}
        async with session.get(
            f"{STRAPIURL}/customers", headers=headers, params=params
        ) as resp:
            if resp.status != 200:
                logger.error(f"Ошибка поиска customer: {resp.status}")
                return False

            data = await resp.json()
            if not data.get("data"):
                logger.warning(f"Customer с tg_id {tg_id} не найден")
                return False

            customer = data["data"][0]
            customer_id = customer["documentId"]

        payload = {"data": {"email": email}}
        update_url = f"{STRAPIURL}/customers/{customer_id}"

        async with session.put(update_url, json=payload, headers=headers) as resp:
            if resp.status in (200, 201):
                logger.info(f"Email {email} сохранён для tg_{tg_id}")
                return True
            else:
                logger.error(
                    f"Ошибка обновления email: {resp.status} {await resp.text()}"
                )
                return False
