from typing import Any, Sequence

from fastapi import Depends
from project.database import get_db
from project.models import Dish, Menu, Submenu
from project.services_overal import validate_menu
from sqlalchemy import Row, RowMapping, delete, distinct, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .schemas import MenuInSchema, MenuOutSchema


class MenuRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def read_menu(self, target_menu_id: str) -> MenuOutSchema:
        await validate_menu(db=self.db, target_menu_id=target_menu_id)
        q = (
            select(
                Menu,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .where(Menu.id == target_menu_id)
            .outerjoin(Submenu, Submenu.menu_id == Menu.id)
            .outerjoin(Dish, Dish.submenu_id == Submenu.id)
            .group_by(Menu.id)
        )
        res_q = await self.db.execute(q)
        result = res_q.one_or_none()
        return MenuOutSchema(
            id=result.Menu.id,
            title=result.Menu.title,
            description=result.Menu.description,
            submenus_count=result.submenus_count,
            dishes_count=result.dishes_count,
        )

    async def read_menus(self) -> list[MenuOutSchema]:
        q = (
            select(
                Menu,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)
            .outerjoin(Dish, Dish.submenu_id == Submenu.id)
            .group_by(Menu.id)
        )
        res_q = await self.db.execute(q)
        menus_result = res_q.all()
        return [
            MenuOutSchema(
                id=result.Menu.id,
                title=result.Menu.title,
                description=result.Menu.description,
                submenus_count=result.submenus_count,
                dishes_count=result.dishes_count,
            )
            for result in menus_result
        ]

    async def read_menus_whole(self) -> Sequence[Row | RowMapping | Any]:
        q = select(Menu).options(
            selectinload(Menu.submenus).options(selectinload(Submenu.dishes))
        )

        res_q = await self.db.execute(q)
        menus_result = res_q.scalars().all()
        return menus_result

    async def create_menu(self, menu: MenuInSchema) -> MenuOutSchema:
        insert_menu_query = await self.db.execute(
            insert(Menu).values(
                title=menu.title,
                description=menu.description,
            )
        )
        new_menu_id = insert_menu_query.inserted_primary_key[0]
        await self.db.commit()
        q = await self.db.execute(select(Menu).where(Menu.id == new_menu_id))
        inserted_menu = q.scalars().one_or_none()
        return MenuOutSchema(
            id=str(inserted_menu.id),
            title=inserted_menu.title,
            description=inserted_menu.description,
            submenus_count=0,
            dishes_count=0,
        )

    async def update_menu(
        self, target_menu_id: str, menu: MenuInSchema
    ) -> MenuOutSchema:
        await validate_menu(db=self.db, target_menu_id=target_menu_id)

        await self.db.execute(
            update(Menu)
            .values(title=menu.title, description=menu.description)
            .where(Menu.id == target_menu_id)
        )
        await self.db.commit()

        return await self.read_menu(target_menu_id=target_menu_id)

    async def del_menu(self, target_menu_id: str) -> dict[str, bool | str]:
        await validate_menu(db=self.db, target_menu_id=target_menu_id)
        await self.db.execute(delete(Menu).where(Menu.id == target_menu_id))
        await self.db.commit()
        return {'status': True, 'message': 'The menu has been deleted'}
