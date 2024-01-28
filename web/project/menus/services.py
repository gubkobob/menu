from sqlalchemy import delete, distinct, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..exeptions import NotFoundException
from ..models import Dish, Menu, Submenu


async def get_menu(session: AsyncSession, target_menu_id: str) -> dict:
    q = (
        select(
            Menu.id,
            Menu.title,
            Menu.description,
            func.count(distinct(Submenu.id)).label("submenus_count"),
            func.count(distinct(Dish.id)).label("dishes_count"),
        )
        .where(Menu.id == target_menu_id)
        .outerjoin(Submenu, Submenu.menu_id == Menu.id)
        .outerjoin(Dish, Dish.submenu_id == Submenu.id)
        .group_by(Menu.id)
    )
    res_q = await session.execute(q)
    result = res_q.one_or_none()
    if not result:
        raise NotFoundException(error_type="NO MENU", error_message="menu not found")
    return result


async def get_menus(session: AsyncSession) -> list:
    q = (
        select(
            Menu.id,
            Menu.title,
            Menu.description,
            func.count(distinct(Submenu.id)).label("submenus_count"),
            func.count(distinct(Dish.id)).label("dishes_count"),
        )
        .outerjoin(Submenu, Menu.id == Submenu.menu_id)
        .outerjoin(Dish, Dish.submenu_id == Submenu.id)
        .group_by(Menu.id)
    )
    res_q = await session.execute(q)
    menus = res_q.all()

    return menus


async def post_menu(session: AsyncSession, title: str, description: str) -> dict:
    insert_menu_query = await session.execute(
        insert(Menu).values(
            title=title,
            description=description,
        )
    )
    new_menu_id = insert_menu_query.inserted_primary_key[0]
    await session.commit()
    q = await session.execute(select(Menu).where(Menu.id == new_menu_id))
    inserted_menu = q.scalars().one_or_none()

    return inserted_menu


async def delete_menu(session: AsyncSession, target_menu_id: str):
    await get_menu(session=session, target_menu_id=target_menu_id)
    await session.execute(delete(Menu).where(Menu.id == target_menu_id))
    await session.commit()


async def change_menu(
    session: AsyncSession, target_menu_id: str, title: str, description: str
) -> dict:
    await get_menu(session=session, target_menu_id=target_menu_id)

    await session.execute(
        update(Menu)
        .values(title=title, description=description)
        .where(Menu.id == target_menu_id)
    )
    await session.commit()

    q = await session.execute(select(Menu).where(Menu.id == target_menu_id))
    changed_menu = q.scalars().one_or_none()
    return changed_menu
