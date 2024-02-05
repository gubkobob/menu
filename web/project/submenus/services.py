from typing import Sequence

from project.database import get_redis_client
from project.exeptions import NotFoundException

# from project.menus.services import get_menu
from project.models import Dish, Menu, Submenu
from project.services_overal import RedisCache
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

cache = RedisCache(get_redis_client())


async def get_submenu(
    db: AsyncSession, target_menu_id: str, target_submenu_id: str
) -> Submenu:
    # await get_menu(db=db, target_menu_id=target_menu_id)
    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    data = cache.get_data_from_cache(key=key_submenu)
    if data is not None:
        result = data
    else:
        q = await db.execute(
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
        cache.set_data_to_cache(key=key_submenu, value=result)
    return result


async def get_submenus(db: AsyncSession, target_menu_id: str) -> Sequence[Submenu]:
    # await get_menu(db=db, target_menu_id=target_menu_id)
    key_submenus = '/'.join([target_menu_id, 'submenus'])
    data = cache.get_data_from_cache(key=key_submenus)
    if data is not None:
        submenus = data
    else:
        q = await db.execute(
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
        cache.set_data_to_cache(key=key_submenus, value=submenus)
    return submenus


async def post_submenu(
    db: AsyncSession, target_menu_id: str, title: str, description: str
) -> Submenu:
    # menu = await get_menu(db=db, target_menu_id=target_menu_id)

    insert_submenu_query = await db.execute(
        insert(Submenu).values(title=title, description=description, menu_id=target_menu_id)
    )
    new_submenu_id = insert_submenu_query.inserted_primary_key[0]
    await db.commit()
    q = await db.execute(select(Submenu).where(Submenu.id == new_submenu_id))
    inserted_submenu = q.scalars().one_or_none()

    key_submenus = '/'.join([target_menu_id, 'submenus'])
    cache.delete_data_from_cache('all_menus', target_menu_id, key_submenus)

    return inserted_submenu


async def delete_submenu(db: AsyncSession, target_menu_id: str, target_submenu_id: str):
    await get_submenu(
        db=db,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
    )
    await db.execute(
        delete(Submenu).where(
            Submenu.id == target_submenu_id, Submenu.menu_id == target_menu_id
        )
    )
    await db.commit()
    key_submenus = '/'.join([target_menu_id, 'submenus'])
    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    cache.delete_data_from_cache('all_menus', target_menu_id, key_submenu, key_submenus)
    cache.clear_namespace_from_cache(key_submenu)


async def change_submenu(
    db: AsyncSession,
    target_menu_id: str,
    target_submenu_id: str,
    title: str,
    description: str,
) -> Submenu:
    await get_submenu(
        db=db,
        target_submenu_id=target_submenu_id,
        target_menu_id=target_menu_id,
    )

    await db.execute(
        update(Submenu)
        .values(title=title, description=description)
        .where(Submenu.id == target_submenu_id)
    )
    await db.commit()

    q = await db.execute(select(Submenu).where(Submenu.id == target_submenu_id))
    changed_submenu = q.scalars().one_or_none()

    key_submenu = '/'.join([target_menu_id, target_submenu_id])
    key_submenus = '/'.join([target_menu_id, 'submenus'])
    cache.delete_data_from_cache(key_submenu, key_submenus)
    return changed_submenu
