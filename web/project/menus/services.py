
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..exeptions import  NotFoundException
from .schemas import MenuOutSchema
from ..models import Menu


async def get_menu(session: AsyncSession, target_menu_id: str) -> dict:
    q = await session.execute(
        select(Menu).where(Menu.id == target_menu_id)
    )
    menu = q.scalars().one_or_none()
    if not menu:
        raise NotFoundException(
            error_type="NO MENU", error_message="menu not found"
        )
    return menu


async def get_menus(session: AsyncSession) -> list:
    q = await session.execute(select(Menu))
    menus = q.scalars().all()
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