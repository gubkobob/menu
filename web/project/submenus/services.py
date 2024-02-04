from typing import Sequence

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..exeptions import NotFoundException
from ..menus.services import get_menu
from ..models import Dish, Menu, Submenu
from ..services_overal import (
    clear_namespace_from_cache,
    delete_data_from_cache,
    get_data_from_cache,
    set_data_to_cache,
)


async def get_submenu(
    session: AsyncSession, target_menu_id: str, target_submenu_id: str
) -> Submenu:
    await get_menu(session=session, target_menu_id=target_menu_id)
    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    data = get_data_from_cache(key=key_submenu)
    if data is not None:
        result = data
    else:
        q = await session.execute(
            select(
                Submenu.id,
                Submenu.description,
                Submenu.title,
                func.count(Dish.id).label('dishes_count'),
            )
            .where(Submenu.id == target_submenu_id, Submenu.menu_id == target_menu_id)
            .join(Dish, isouter=True)
            .group_by(Submenu.id)
        )
        result = q.one_or_none()
        if not result:
            raise NotFoundException(
                error_type='NO SUBMENU', error_message='submenu not found'
            )
        set_data_to_cache(key=key_submenu, value=result)
    return result


async def get_submenus(session: AsyncSession, target_menu_id: str) -> Sequence[Submenu]:
    await get_menu(session=session, target_menu_id=target_menu_id)
    key_submenus = '/'.join([target_menu_id, 'submenus'])
    data = get_data_from_cache(key=key_submenus)
    if data is not None:
        submenus = data
    else:
        q = await session.execute(
            select(
                Submenu.id,
                Submenu.description,
                Submenu.title,
                func.count(Dish.id).label('dishes_count'),
            )
            .join(Dish, isouter=True)
            .where(Submenu.menu.has(Menu.id == target_menu_id))
            .group_by(Submenu.id)
        )
        submenus = q.all()
        set_data_to_cache(key=key_submenus, value=submenus)
    return submenus


async def post_submenu(
    session: AsyncSession, target_menu_id: str, title: str, description: str
) -> Submenu:
    menu = await get_menu(session=session, target_menu_id=target_menu_id)

    insert_submenu_query = await session.execute(
        insert(Submenu).values(title=title, description=description, menu_id=menu.id)
    )
    new_submenu_id = insert_submenu_query.inserted_primary_key[0]
    await session.commit()
    q = await session.execute(select(Submenu).where(Submenu.id == new_submenu_id))
    inserted_submenu = q.scalars().one_or_none()

    key_submenus = '/'.join([target_menu_id, 'submenus'])
    delete_data_from_cache('all_menus', target_menu_id, key_submenus)

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
    key_submenus = '/'.join([target_menu_id, 'submenus'])
    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    delete_data_from_cache('all_menus', target_menu_id, key_submenu, key_submenus)
    clear_namespace_from_cache(key_submenu)


async def change_submenu(
    session: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    title: str,
    description: str,
) -> Submenu:
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

    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    key_submenus = '/'.join([target_menu_id, 'submenus'])
    delete_data_from_cache(key_submenu, key_submenus)
    return changed_submenu
