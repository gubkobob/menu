from fastapi import Depends
from project.database import get_db
from project.menus.schemas import MenuInSchema
from project.models import Dish, Submenu
from project.services_overal import validate_menu, validate_submenu
from sqlalchemy import delete, distinct, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import SubMenuOutSchema


class SubmenuRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def read_submenu(
        self, target_menu_id: str, target_submenu_id: str
    ) -> SubMenuOutSchema:
        await validate_submenu(
            db=self.db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
        )
        q = await self.db.execute(
            select(
                Submenu,
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .where(Submenu.id == target_submenu_id)
            .outerjoin(Dish, Dish.submenu_id == Submenu.id)
            .group_by(Submenu.id)
        )
        result = q.one_or_none()
        return SubMenuOutSchema(
            id=result.Submenu.id,
            title=result.Submenu.title,
            description=result.Submenu.description,
            dishes_count=result.dishes_count,
        )

    async def read_submenus(self, target_menu_id: str) -> list[SubMenuOutSchema]:
        await validate_menu(db=self.db, target_menu_id=target_menu_id)
        q = await self.db.execute(
            select(
                Submenu,
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .where(Submenu.menu_id == target_menu_id)
            .outerjoin(Dish, Dish.submenu_id == Submenu.id)
            .group_by(Submenu.id)
        )
        submenus = q.all()
        print(submenus)
        return [
            SubMenuOutSchema(
                id=result.Submenu.id,
                title=result.Submenu.title,
                description=result.Submenu.description,
                dishes_count=result.dishes_count,
            )
            for result in submenus
        ]

    async def create_submenu(
        self, target_menu_id: str, submenu: MenuInSchema
    ) -> SubMenuOutSchema:
        await validate_menu(db=self.db, target_menu_id=target_menu_id)
        insert_submenu_query = await self.db.execute(
            insert(Submenu).values(
                title=submenu.title,
                description=submenu.description,
                menu_id=target_menu_id,
            )
        )
        new_submenu_id = insert_submenu_query.inserted_primary_key[0]
        await self.db.commit()
        q = await self.db.execute(select(Submenu).where(Submenu.id == new_submenu_id))
        inserted_submenu = q.scalars().one_or_none()
        return SubMenuOutSchema(
            id=str(inserted_submenu.id),
            title=inserted_submenu.title,
            description=inserted_submenu.description,
            dishes_count=0,
        )

    async def update_submenu(
        self, target_menu_id: str, target_submenu_id: str, submenu: MenuInSchema
    ) -> SubMenuOutSchema:
        await validate_submenu(
            db=self.db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
        )

        await self.db.execute(
            update(Submenu)
            .values(title=submenu.title, description=submenu.description)
            .where(Submenu.id == target_submenu_id)
        )
        await self.db.commit()

        return await self.read_submenu(
            target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
        )

    async def del_submenu(self, target_menu_id: str, target_submenu_id: str) -> dict:
        await validate_submenu(
            db=self.db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
        )
        await self.db.execute(delete(Submenu).where(Submenu.id == target_submenu_id))
        await self.db.commit()
        return {'status': True, 'message': 'The submenu has been deleted'}
