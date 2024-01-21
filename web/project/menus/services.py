
from sqlalchemy import select, insert, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from ..exeptions import  NotFoundException
from .schemas import MenuOutSchema
from ..models import Menu, Submenu, Dish


async def get_menu(session: AsyncSession, target_menu_id: str) -> dict:

    q = (
        select(
            Menu,
            func.count(Submenu.id).label("submenus_count"),
            func.count(Dish.id).label("dishes_count"),
        )
         .where(Menu.id == target_menu_id)
         .join(Submenu, Submenu.menu_id == Menu.id, isouter=True)
         .join(Dish, Dish.submenu_id == Submenu.id, isouter=True)
         .group_by(Menu.id)
         )
    res_q = await session.execute(q)
    result = res_q.one_or_none()
    if not result:
        raise NotFoundException(
            error_type="NO MENU", error_message="menu not found"
        )
    menu = result[0]
    count_submenu = result[1]
    count_dishes = result[2]
    menu.submenus_count = count_submenu
    menu.dishes_count = count_dishes

    print("*******************************************")
    print(res_q)
    print(result)
    print(menu)
    print(count_submenu)
    print(q)
    print("*******************************************")


    return menu


async def get_menus(session: AsyncSession) -> list:

    q = (select(Menu, func.count(Submenu.id).label("submenus_count"), func.count(Dish.id).label("dishes_count"))
         .join(Submenu, isouter=True,)
         .join(Submenu, Submenu.menu_id == Menu.id, isouter=True)
         .join(Dish, Dish.submenu_id == Submenu.id, isouter=True)
         .group_by(Menu.id)
         )
    res_q = await session.execute(q)
    results = res_q.all()
    menus = []
    for result in results:
        menu = result[0]
        count_submenu = result[1]
        menu.submenus_count = count_submenu
        menus.append(menu)
    print("*******************************************")
    print(results)
    print("*******************************************")
    return menus


async def post_menu(
    session: AsyncSession, title: str, description: str
) -> dict:

    insert_menu_query = await session.execute(
        insert(Menu).values(
            title=title,
            description=description,
        )
    )
    new_menu_id = insert_menu_query.inserted_primary_key[0]
    await session.commit()
    q = await session.execute(
        select(Menu).where(Menu.id == new_menu_id)
    )
    inserted_menu = q.scalars().one_or_none()

    return inserted_menu

async def delete_menu(session: AsyncSession, target_menu_id: str):
    await get_menu(session=session, target_menu_id=target_menu_id)
    await session.execute(
        delete(Menu).where(Menu.id == target_menu_id)
    )
    await session.commit()


async def change_menu(
    session: AsyncSession, target_menu_id: str, title: str, description: str
) -> dict:

    await get_menu(session=session, target_menu_id=target_menu_id)

    await session.execute(update(Menu).values(title=title, description=description).where(Menu.id == target_menu_id))
    await session.commit()

    q = await session.execute(
        select(Menu).where(Menu.id == target_menu_id)
    )
    changed_menu = q.scalars().one_or_none()
    return changed_menu