import pickle

from project.database import async_session, get_async_redis_client
from project.models import Dish, Menu, Submenu
from sqlalchemy import delete, select

MenuType = tuple[str, str, str]
SubmenuType = tuple[str, str, str, str]
DishType = tuple[str, str, str, str, str, str, str | float | None]


def get_menus_ids_from_data(menus: list[MenuType]) -> list[str]:
    ids = []
    for menu in menus:
        ids.append(menu[0])
    return ids


async def update_menu_data_from_file_to_db(menus: list[MenuType]) -> None:
    for menu in menus:
        await update_or_create_menu(menu=menu)
    await delete_menus_not_in_data(menus=menus)


async def update_or_create_menu(menu: MenuType) -> None:
    async with async_session() as session:
        result = await session.execute(select(Menu).filter(Menu.id == menu[0]))
        db_menu = result.scalar_one_or_none()
        if db_menu:
            db_menu.title = menu[1]
            db_menu.description = menu[2]
            await session.commit()
        else:
            db_menu = Menu(title=menu[1], description=menu[2], id=menu[0])
            session.add(db_menu)
            await session.commit()


async def delete_menus_not_in_data(menus: list[MenuType]) -> None:
    menus_ids_from_data = get_menus_ids_from_data(menus=menus)
    async with async_session() as session:
        result = await session.execute(select(Menu.id))
    menus_ids_from_db = result.scalars().all()
    async with async_session() as session:
        for menu_id in menus_ids_from_db:
            if menu_id not in menus_ids_from_data:
                await session.execute(delete(Menu).where(Menu.id == menu_id))
        await session.commit()


def get_submenus_ids_from_data(submenus: list[SubmenuType]) -> list[str]:
    ids = []
    for submenu in submenus:
        ids.append(submenu[1])
    return ids


async def update_submenu_data_from_file_to_db(submenus: list[SubmenuType]) -> None:
    for submenu in submenus:
        await update_or_create_submenu(submenu=submenu)
    await delete_submenus_not_in_data(submenus=submenus)


async def update_or_create_submenu(submenu: SubmenuType) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(Submenu).filter(
                Submenu.id == submenu[1], Submenu.menu_id == submenu[0]
            )
        )
        db_submenu = result.scalar_one_or_none()
        if db_submenu:
            db_submenu.title = submenu[2]
            db_submenu.description = submenu[3]
            await session.commit()
        else:
            db_submenu = Submenu(
                title=submenu[2],
                description=submenu[3],
                id=submenu[1],
                menu_id=submenu[0],
            )
            session.add(db_submenu)
            await session.commit()


async def delete_submenus_not_in_data(submenus: list[SubmenuType]) -> None:
    submenus_ids_from_data = get_submenus_ids_from_data(submenus=submenus)
    async with async_session() as session:
        result = await session.execute(select(Submenu.id))
    submenus_ids_from_db = result.scalars().all()
    async with async_session() as session:
        for submenu_id in submenus_ids_from_db:
            if submenu_id not in submenus_ids_from_data:
                await session.execute(delete(Submenu).where(Submenu.id == submenu_id))
        await session.commit()


def get_dishes_ids_from_data(dishes: list[DishType]) -> list[str]:
    ids = []
    for dish in dishes:
        ids.append(dish[2])
    return ids


async def update_dish_data_from_file_to_db(dishes: list[DishType]) -> None:
    for dish in dishes:
        await update_or_create_dish(dish=dish)
    await delete_dishes_not_in_data(dishes=dishes)


async def update_or_create_dish(dish: DishType) -> None:
    redis_client = await get_async_redis_client()
    if dish[6]:
        key_discount = '/'.join([dish[2], 'discount'])
        val_bytes = pickle.dumps(dish[6])
        await redis_client.set(key_discount, val_bytes)

    async with async_session() as session:
        result = await session.execute(
            select(Dish).filter(Dish.id == dish[2], Dish.submenu_id == dish[1])
        )
        db_dish = result.scalar_one_or_none()
        if db_dish:
            db_dish.title = dish[3]
            db_dish.description = dish[4]
            db_dish.price = dish[5]
            await session.commit()
        else:
            db_dish = Dish(
                title=dish[3],
                description=dish[4],
                id=dish[2],
                submenu_id=dish[1],
                price=dish[5],
            )
            session.add(db_dish)
            await session.commit()


async def delete_dishes_not_in_data(dishes: list[DishType]) -> None:
    dishes_ids_from_data = get_dishes_ids_from_data(dishes=dishes)
    async with async_session() as session:
        result = await session.execute(select(Dish.id))
    dishes_ids_from_db = result.scalars().all()
    async with async_session() as session:
        for dish_id in dishes_ids_from_db:
            if dish_id not in dishes_ids_from_data:
                await session.execute(delete(Dish).where(Dish.id == dish_id))
        await session.commit()
