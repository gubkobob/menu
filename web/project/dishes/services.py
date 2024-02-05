from typing import Sequence

from project.database import get_redis_client
from project.exeptions import NotFoundException
from project.models import Dish, Submenu
from project.services_overal import RedisCache
from project.submenus.services import get_submenu
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

cache = RedisCache(get_redis_client())


async def get_dish(
    db: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
) -> Dish:
    await get_submenu(
        db=db,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
    )
    key_dish = '/'.join([target_menu_id, target_submenu_id, target_dish_id])
    data = cache.get_data_from_cache(key=key_dish)
    if data is not None:
        dish = data
    else:
        q = await db.execute(
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
        cache.set_data_to_cache(key=key_dish, value=dish)
    return dish


async def get_dishes(
    db: AsyncSession, target_menu_id: str, target_submenu_id: str
) -> Sequence[Dish]:
    key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
    data = cache.get_data_from_cache(key=key_dishes)
    if data is not None:
        dishes = data
    else:
        q = await db.execute(
            select(Dish).where(
                Dish.submenu_id == target_submenu_id,
                Dish.submenu.has(Submenu.menu_id == target_menu_id),
            )
        )
        dishes = q.scalars().all()
        if not dishes:
            dishes = []
        cache.set_data_to_cache(key=key_dishes, value=dishes)
    return dishes


async def post_dish(
    db: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    title: str,
    description: str,
    price: str,
) -> Dish:
    await get_submenu(
        db=db,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
    )

    insert_dish_query = await db.execute(
        insert(Dish).values(
            title=title,
            description=description,
            price=price,
            submenu_id=target_submenu_id,
        )
    )
    new_dish_id = insert_dish_query.inserted_primary_key[0]
    await db.commit()
    q = await db.execute(select(Dish).where(Dish.id == new_dish_id))
    inserted_dish = q.scalars().one_or_none()

    key_submenus = '/'.join([target_menu_id, 'submenus'])
    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])

    cache.delete_data_from_cache(
        'all_menus', target_menu_id, key_submenu, key_submenus, key_dishes
    )
    return inserted_dish


async def delete_dish(
    db: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
):
    await get_dish(
        db=db,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        target_dish_id=target_dish_id,
    )
    await db.execute(delete(Dish).where(Dish.id == target_dish_id))
    await db.commit()

    key_submenus = '/'.join([target_menu_id, 'submenus'])
    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
    key_dish = '/'.join([target_menu_id, target_submenu_id, target_dish_id])

    cache.delete_data_from_cache(
        'all_menus', target_menu_id, key_submenu, key_submenus, key_dishes, key_dish
    )


async def change_dish(
    db: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    title: str,
    description: str,
    price: str,
) -> Dish:
    await get_dish(
        db=db,
        target_submenu_id=target_submenu_id,
        target_menu_id=target_menu_id,
        target_dish_id=target_dish_id,
    )

    await db.execute(
        update(Dish)
        .values(title=title, description=description, price=price)
        .where(Dish.id == target_dish_id)
    )
    await db.commit()

    q = await db.execute(select(Dish).where(Dish.id == target_dish_id))
    changed_dish = q.scalars().one_or_none()

    key_dish = '/'.join([target_menu_id, target_submenu_id, target_dish_id])
    key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
    cache.delete_data_from_cache(
        key_dishes,
        key_dish,
    )

    return changed_dish
