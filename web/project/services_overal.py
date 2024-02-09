from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Dish, Menu, Submenu


async def validate_menu(db: AsyncSession, target_menu_id: str):
    res_q = await db.execute(select(Menu).where(Menu.id == target_menu_id))
    result = res_q.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail='menu not found')


async def validate_submenu(
    db: AsyncSession, target_menu_id: str, target_submenu_id: str
):
    await validate_menu(db=db, target_menu_id=target_menu_id)
    res_q = await db.execute(select(Submenu).where(Submenu.id == target_submenu_id))
    result = res_q.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail='submenu not found')


async def validate_dish(
    db: AsyncSession, target_menu_id: str, target_submenu_id: str, target_dish_id: str
):
    await validate_submenu(
        db=db, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
    )
    res_q = await db.execute(select(Dish).where(Dish.id == target_dish_id))
    result = res_q.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail='dish not found')
