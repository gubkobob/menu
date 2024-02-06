import redis
from fastapi import Depends
from project.database import get_redis_client
from project.services_overal import RedisCache

from .repository import MenuRepository
from .schemas import MenuInSchema, MenuOutSchema


class MenuService:
    def __init__(
        self,
        menu_repository: MenuRepository = Depends(),
        redis_client: redis.Redis = Depends(get_redis_client),
    ):
        self.menu_repository = menu_repository
        self.cache = RedisCache(redis_client)

    async def read_menu(self, target_menu_id: str) -> MenuOutSchema:
        data = self.cache.get_data_from_cache(key=target_menu_id)
        if data is not None:
            return data
        result = await self.menu_repository.read_menu(target_menu_id=target_menu_id)
        self.cache.set_data_to_cache(key=target_menu_id, value=result)
        return result

    async def read_menus(self) -> list[MenuOutSchema]:
        data = self.cache.get_data_from_cache(key='all_menus')
        if data is not None:
            return data
        result = await self.menu_repository.read_menus()
        self.cache.set_data_to_cache(key='all_menus', value=result)
        return result

    async def create_menu(self, menu: MenuInSchema) -> MenuOutSchema:
        result = await self.menu_repository.create_menu(menu=menu)
        self.cache.delete_data_from_cache('all_menus')
        return result

    async def del_menu(self, target_menu_id: str) -> dict[str, str | bool]:
        result = await self.menu_repository.del_menu(target_menu_id=target_menu_id)
        self.cache.delete_data_from_cache('all_menus')
        self.cache.clear_namespace_from_cache(target_menu_id)
        return result

    async def update_menu(
        self, target_menu_id: str, menu: MenuInSchema
    ) -> MenuOutSchema:
        changed_menu = await self.menu_repository.update_menu(
            target_menu_id=target_menu_id, menu=menu
        )
        self.cache.delete_data_from_cache(target_menu_id, 'all_menus')
        return changed_menu
