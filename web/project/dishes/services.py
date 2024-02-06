import redis
from fastapi import Depends
from project.database import get_redis_client
from project.services_overal import RedisCache

from .repository import DishRepository
from .schemas import DishInSchema, DishOutSchema


class DishService:
    def __init__(
        self,
        dish_repository: DishRepository = Depends(),
        redis_client: redis.Redis = Depends(get_redis_client),
    ):
        self.dish_repository = dish_repository
        self.cache = RedisCache(redis_client)

    async def read_dish(
        self,
        target_menu_id: str,
        target_submenu_id: str,
        target_dish_id: str,
    ) -> DishOutSchema:
        key_dish = '/'.join([target_menu_id, target_submenu_id, target_dish_id])
        data = self.cache.get_data_from_cache(key=key_dish)
        if data is not None:
            return data
        result = await self.dish_repository.read_dish(
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )
        # self.cache.set_data_to_cache(key=key_dish, value=result)
        return result

    async def read_dishes(
        self, target_menu_id: str, target_submenu_id: str
    ) -> list[DishOutSchema]:
        key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
        data = self.cache.get_data_from_cache(key=key_dishes)
        if data is not None:
            return data
        result = await self.dish_repository.read_dishes(
            target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
        )
        self.cache.set_data_to_cache(key=key_dishes, value=result)
        return result

    async def create_dish(
        self,
        target_menu_id: str,
        target_submenu_id: str,
        dish: DishInSchema,
    ) -> DishOutSchema:
        result = await self.dish_repository.create_dish(
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            dish=dish,
        )
        key_submenus = '/'.join([target_menu_id, 'submenus'])
        key_submenu = '/'.join([target_menu_id, target_submenu_id])
        key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
        self.cache.delete_data_from_cache(
            'all_menus', target_menu_id, key_submenu, key_submenus, key_dishes
        )
        return result

    async def del_dish(
        self,
        target_menu_id: str,
        target_submenu_id: str,
        target_dish_id: str,
    ) -> dict:
        return await self.dish_repository.del_dish(
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )
        key_submenus = '/'.join([target_menu_id, 'submenus'])
        key_submenu = '/'.join([target_menu_id, target_submenu_id])
        key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
        key_dish = '/'.join([target_menu_id, target_submenu_id, target_dish_id])
        self.cache.delete_data_from_cache(
            'all_menus', target_menu_id, key_submenu, key_submenus, key_dishes, key_dish
        )

    async def update_dish(
        self,
        target_menu_id: str,
        target_submenu_id: str,
        target_dish_id: str,
        dish: DishInSchema,
    ) -> DishOutSchema:
        result = await self.dish_repository.update_dish(
            target_menu_id=target_menu_id,
            target_dish_id=target_dish_id,
            target_submenu_id=target_submenu_id,
            dish=dish,
        )
        key_dish = '/'.join([target_menu_id, target_submenu_id, target_dish_id])
        key_dishes = '/'.join([target_menu_id, target_submenu_id, 'dishes'])
        self.cache.delete_data_from_cache(
            key_dishes,
            key_dish,
        )
        return result
