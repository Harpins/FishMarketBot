import aiohttp
from datetime import datetime
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

