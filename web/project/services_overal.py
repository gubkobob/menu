from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_async_redis_client
from .models import Dish, Menu, Submenu
from .service_redis import AsyncRedisCache


async def validate_menu(db: AsyncSession, target_menu_id: str) -> None:
    res_q = await db.execute(select(Menu).where(Menu.id == target_menu_id))
    result = res_q.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail='menu not found')


async def validate_submenu(
    db: AsyncSession, target_menu_id: str, target_submenu_id: str
) -> None:
    await validate_menu(db=db, target_menu_id=target_menu_id)
    res_q = await db.execute(
        select(Submenu).where(
            Submenu.id == target_submenu_id, Submenu.menu_id == target_menu_id
        )
    )
    result = res_q.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail='submenu not found')


async def validate_dish(
    db: AsyncSession, target_menu_id: str, target_submenu_id: str, target_dish_id: str
) -> None:
    await validate_submenu(
        db=db, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
    )
    res_q = await db.execute(
        select(Dish).where(
            Dish.id == target_dish_id, Dish.submenu_id == target_submenu_id
        )
    )
    result = res_q.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail='dish not found')


async def get_dish_price_with_discount(dish_id: str, dish_price: str) -> str:
    redis_cl = await get_async_redis_client()
    redis_client = AsyncRedisCache(redis_cl)
    key_discount = '/'.join([dish_id, 'discount'])
    discount = await redis_client.get_data_from_cache(key=key_discount)
    if discount:
        price_float = float(dish_price) * (100 - float(discount)) / 100
        price = str(round(price_float, 2))
    else:
        price = str(dish_price)
    return price
