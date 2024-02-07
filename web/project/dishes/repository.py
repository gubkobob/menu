from fastapi import Depends
from project.database import get_db
from project.models import Dish
from project.services_overal import validate_dish, validate_submenu
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import DishInSchema, DishOutSchema


class DishRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def read_dish(
        self, target_menu_id: str, target_submenu_id: str, target_dish_id: str
    ) -> DishOutSchema:
        await validate_dish(
            db=self.db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )
        q = await self.db.execute(select(Dish).where(Dish.id == target_dish_id))
        result = q.one_or_none()
        return DishOutSchema(
            id=result.Dish.id,
            title=result.Dish.title,
            description=result.Dish.description,
            price=result.Dish.price,
        )

    async def read_dishes(
        self, target_menu_id: str, target_submenu_id: str
    ) -> list[DishOutSchema]:
        q = await self.db.execute(
            select(Dish).where(
                Dish.submenu_id == target_submenu_id,
            )
        )
        dishes_result = q.all()
        if not dishes_result:
            return []
        return [
            DishOutSchema(
                id=result.Dish.id,
                title=result.Dish.title,
                description=result.Dish.description,
                price=result.Dish.price,
            )
            for result in dishes_result
        ]

    async def create_dish(
        self, target_menu_id: str, target_submenu_id: str, dish: DishInSchema
    ) -> DishOutSchema:
        await validate_submenu(
            db=self.db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
        )
        insert_dish_query = await self.db.execute(
            insert(Dish).values(
                title=dish.title,
                description=dish.description,
                price=dish.price,
                submenu_id=target_submenu_id,
            )
        )
        new_dish_id = insert_dish_query.inserted_primary_key[0]
        await self.db.commit()
        q = await self.db.execute(select(Dish).where(Dish.id == new_dish_id))
        inserted_dish = q.scalars().one_or_none()
        return DishOutSchema(
            id=inserted_dish.id,
            title=inserted_dish.title,
            description=inserted_dish.description,
            price=inserted_dish.price,
        )

    async def update_dish(
        self,
        target_menu_id: str,
        target_submenu_id: str,
        target_dish_id: str,
        dish: DishInSchema,
    ) -> DishOutSchema:
        await validate_dish(
            db=self.db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )
        await self.db.execute(
            update(Dish)
            .values(title=dish.title, description=dish.description, price=dish.price)
            .where(Dish.id == target_dish_id)
        )
        await self.db.commit()

        return await self.read_dish(
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )

    async def del_dish(
        self, target_menu_id: str, target_submenu_id: str, target_dish_id: str
    ) -> dict[str, str | bool]:
        await validate_dish(
            db=self.db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )
        await self.db.execute(delete(Dish).where(Dish.id == target_dish_id))
        await self.db.commit()
        return {'status': True, 'message': 'The dish has been deleted'}
