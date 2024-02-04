from typing import Sequence

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..exeptions import NotFoundException
from ..models import Dish, Submenu
from ..services_overal import (
    delete_data_from_cache,
    get_data_from_cache,
    set_data_to_cache,
)
from ..submenus.services import get_submenu


async def get_dish(
    session: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
) -> Dish:
    await get_submenu(
        session=session,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
    )
    key_dish = '/'.join([target_menu_id, target_submenu_id, target_dish_id])
    data = get_data_from_cache(key=key_dish)
    if data is not None:
        dish = data
    else:
        q = await session.execute(
            select(Dish).where(
                Dish.id == target_dish_id,
                Dish.submenu_id == target_submenu_id,
                Dish.submenu.has(Submenu.menu_id == target_menu_id),
            )
        )
        dish = q.scalars().one_or_none()
        if not dish:
            raise NotFoundException(
                error_type='NO DISH', error_message='dish not found'
            )
        set_data_to_cache(key=key_dish, value=dish)
    return dish


async def get_dishes(
    session: AsyncSession, target_menu_id: str, target_submenu_id: str
) -> Sequence[Dish]:
    key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
    data = get_data_from_cache(key=key_dishes)
    if data is not None:
        dishes = data
    else:
        q = await session.execute(
            select(Dish).where(
                Dish.submenu_id == target_submenu_id,
                Dish.submenu.has(Submenu.menu_id == target_menu_id),
            )
        )
        dishes = q.scalars().all()
        if not dishes:
            dishes = []
        set_data_to_cache(key=key_dishes, value=dishes)
    return dishes


async def post_dish(
    session: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    title: str,
    description: str,
    price: str,
) -> Dish:
    await get_submenu(
        session=session,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
    )

    insert_dish_query = await session.execute(
        insert(Dish).values(
            title=title, description=description, price=price, submenu_id=target_submenu_id
        )
    )
    new_dish_id = insert_dish_query.inserted_primary_key[0]
    await session.commit()
    q = await session.execute(select(Dish).where(Dish.id == new_dish_id))
    inserted_dish = q.scalars().one_or_none()

    key_submenus = '/'.join([target_menu_id, 'submenus'])
    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])

    delete_data_from_cache('all_menus', target_menu_id, key_submenu, key_submenus, key_dishes)
    return inserted_dish


async def delete_dish(
    session: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
):
    await get_dish(
        session=session,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        target_dish_id=target_dish_id,
    )
    await session.execute(delete(Dish).where(Dish.id == target_dish_id))
    await session.commit()

    key_submenus = '/'.join([target_menu_id, 'submenus'])
    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
    key_dish = '/'.join([target_menu_id, target_submenu_id, target_dish_id])

    delete_data_from_cache('all_menus', target_menu_id, key_submenu, key_submenus, key_dishes, key_dish)


async def change_dish(
    session: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    title: str,
    description: str,
    price: str,
) -> Dish:
    await get_dish(
        session=session,
        target_submenu_id=target_submenu_id,
        target_menu_id=target_menu_id,
        target_dish_id=target_dish_id,
    )

    await session.execute(
        update(Dish)
        .values(title=title, description=description, price=price)
        .where(Dish.id == target_dish_id)
    )
    await session.commit()

    q = await session.execute(select(Dish).where(Dish.id == target_dish_id))
    changed_dish = q.scalars().one_or_none()

    key_dish = '/'.join([target_menu_id, target_submenu_id, target_dish_id])
    key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
    delete_data_from_cache(
        key_dishes,
        key_dish,
    )

    return changed_dish
