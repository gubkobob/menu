from decimal import Decimal

from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..exeptions import  NotFoundException

from ..models import Submenu, Dish
from ..submenus.services import get_submenu


async def get_dish(session: AsyncSession, target_menu_id: str, target_submenu_id: str, target_dish_id: str) -> dict:
    await get_submenu(session=session, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id)
    q = await session.execute(
        select(Dish).where(Dish.id == target_dish_id, Dish.submenu_id == target_submenu_id, Dish.submenu.has(Submenu.menu_id == target_menu_id))
    )
    dish = q.scalars().one_or_none()
    if not dish:
        raise NotFoundException(
            error_type="NO DISH", error_message="dish not found"
        )
    return dish


async def get_dishes(session: AsyncSession, target_menu_id: str, target_submenu_id: str) -> list:
    await get_submenu(session=session, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id)
    q = await session.execute(select(Dish).where(Dish.submenu_id == target_submenu_id, Dish.submenu.has(Submenu.menu_id == target_menu_id)))
    dishes = q.scalars().all()
    return dishes


async def post_dish(
    session: AsyncSession, target_menu_id: str, target_submenu_id: str, title: str, description: str, price: str
) -> dict:
    submenu = await get_submenu(session=session, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id)

    insert_dish_query = await session.execute(
        insert(Dish).values(
            title=title,
            description=description,
            price=price,
            submenu_id=submenu.id
        )
    )
    new_dish_id = insert_dish_query.inserted_primary_key[0]
    await session.commit()
    q = await session.execute(
        select(Dish).where(Dish.id == new_dish_id)
    )
    inserted_dish = q.scalars().one_or_none()

    return inserted_dish

async def delete_dish(session: AsyncSession, target_menu_id: str, target_submenu_id: str, target_dish_id: str):
    await get_dish(session=session, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id, target_dish_id=target_dish_id)
    await session.execute(
        delete(Dish).where(Dish.id == target_dish_id)
    )
    await session.commit()


async def change_dish(
    session: AsyncSession, target_menu_id: str, target_submenu_id: str, target_dish_id: str,
        title: str, description: str, price: float
) -> dict:

    await get_dish(session=session, target_submenu_id=target_submenu_id, target_menu_id=target_menu_id, target_dish_id=target_dish_id)

    await session.execute(update(Dish).values(title=title, description=description, price=price).where(Dish.id == target_dish_id))
    await session.commit()

    q = await session.execute(
        select(Dish).where(Dish.id == target_dish_id)
    )
    changed_dish = q.scalars().one_or_none()
    return changed_dish