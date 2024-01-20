
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..exeptions import  NotFoundException
from .schemas import MenuOutSchema
from ..models import Menu


async def get_menu(session: AsyncSession, target_menu_id: int):
    q = await session.execute(
        select(Menu).where(Menu.id == target_menu_id)
    )
    menu = q.scalars().one_or_none()
    if not menu:
        raise NotFoundException(
            error_type="NO MENU", error_message="menu not found"
        )
    return menu


async def get_menus(session: AsyncSession):
    q = await session.execute(select(Menu))
    menus = q.scalars().all()
    return menus


async def post_menu(
    session: AsyncSession, title: str, description: str
) -> MenuOutSchema:

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