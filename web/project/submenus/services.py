from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..exeptions import NotFoundException
from ..menus.services import get_menu
from ..models import Dish, Menu, Submenu


async def get_submenu(
    session: AsyncSession, target_menu_id: str, target_submenu_id: str
) -> dict:
    await get_menu(session=session, target_menu_id=target_menu_id)
    q = await session.execute(
        select(
            Submenu.id,
            Submenu.description,
            Submenu.title,
            func.count(Dish.id).label("dishes_count"),
        )
        .where(Submenu.id == target_submenu_id, Submenu.menu_id == target_menu_id)
        .join(Dish, isouter=True)
        .group_by(Submenu.id)
    )
    result = q.one_or_none()
    if not result:
        raise NotFoundException(
            error_type="NO SUBMENU", error_message="submenu not found"
        )
    return result


async def get_submenus(session: AsyncSession, target_menu_id: str) -> list:
    await get_menu(session=session, target_menu_id=target_menu_id)
    q = await session.execute(
        select(
            Submenu.id,
            Submenu.description,
            Submenu.title,
            func.count(Dish.id).label("dishes_count"),
        )
        .join(Dish, isouter=True)
        .where(Submenu.menu.has(Menu.id == target_menu_id))
        .group_by(Submenu.id)
    )
    submenus = q.all()
    return submenus


async def post_submenu(
    session: AsyncSession, target_menu_id: str, title: str, description: str
) -> dict:
    menu = await get_menu(session=session, target_menu_id=target_menu_id)

    insert_submenu_query = await session.execute(
        insert(Submenu).values(title=title, description=description, menu_id=menu.id)
    )
    new_submenu_id = insert_submenu_query.inserted_primary_key[0]
    await session.commit()
    q = await session.execute(select(Submenu).where(Submenu.id == new_submenu_id))
    inserted_submenu = q.scalars().one_or_none()

    return inserted_submenu


async def delete_submenu(
    session: AsyncSession, target_menu_id: str, target_submenu_id: str
):
    await get_submenu(
        session=session,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
    )
    await session.execute(
        delete(Submenu).where(
            Submenu.id == target_submenu_id, Submenu.menu_id == target_menu_id
        )
    )
    await session.commit()


async def change_submenu(
    session: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    title: str,
    description: str,
) -> dict:
    await get_submenu(
        session=session,
        target_submenu_id=target_submenu_id,
        target_menu_id=target_menu_id,
    )

    await session.execute(
        update(Submenu)
        .values(title=title, description=description)
        .where(Submenu.id == target_submenu_id)
    )
    await session.commit()

    q = await session.execute(select(Submenu).where(Submenu.id == target_submenu_id))
    changed_submenu = q.scalars().one_or_none()
    return changed_submenu
