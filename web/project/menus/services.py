import redis.asyncio as redis
from fastapi import BackgroundTasks, Depends
from project.database import get_async_redis_client
from project.service_redis import AsyncRedisCache

from .repository import MenuRepository
from .schemas import MenuFullListOutSchema, MenuInSchema, MenuOutSchema


class MenuService:
    def __init__(
        self,
        menu_repository: MenuRepository = Depends(),
        redis_client: redis.Redis = Depends(get_async_redis_client),
        background_tasks: BackgroundTasks = None,
    ):
        self.menu_repository = menu_repository
        self.cache = AsyncRedisCache(redis_client)
        self.background_tasks = background_tasks

    async def read_menu(self, target_menu_id: str) -> MenuOutSchema:
        data = await self.cache.get_data_from_cache(key=target_menu_id)
        if data is not None:
            return data
        result = await self.menu_repository.read_menu(target_menu_id=target_menu_id)
        await self.cache.set_data_to_cache(
            key=target_menu_id, value=result, background_tasks=self.background_tasks
        )
        return result

    async def read_menus(self) -> list[MenuOutSchema]:
        data = await self.cache.get_data_from_cache(key='all_menus')
        if data is not None:
            return data
        result = await self.menu_repository.read_menus()
        await self.cache.set_data_to_cache(
            key='all_menus', value=result, background_tasks=self.background_tasks
        )
        return result

    async def create_menu(self, menu: MenuInSchema) -> MenuOutSchema:
        result = await self.menu_repository.create_menu(menu=menu)
        await self.cache.delete_data_from_cache(
            'all_menus', 'all_menus_whole', background_tasks=self.background_tasks
        )
        return result

    async def del_menu(self, target_menu_id: str) -> dict[str, str | bool]:
        result = await self.menu_repository.del_menu(target_menu_id=target_menu_id)
        await self.cache.delete_data_from_cache(
            'all_menus', 'all_menus_whole', background_tasks=self.background_tasks
        )
        await self.cache.clear_namespace_from_cache(
            target_menu_id, background_tasks=self.background_tasks
        )
        return result

    async def update_menu(
        self, target_menu_id: str, menu: MenuInSchema
    ) -> MenuOutSchema:
        changed_menu = await self.menu_repository.update_menu(
            target_menu_id=target_menu_id, menu=menu
        )
        await self.cache.delete_data_from_cache(
            target_menu_id,
            'all_menus',
            'all_menus_whole',
            background_tasks=self.background_tasks,
        )
        return changed_menu

    async def read_menus_whole(self) -> MenuFullListOutSchema:
        data = await self.cache.get_data_from_cache(key='all_menus_whole')
        if data is not None:
            return data
        result = await self.menu_repository.read_menus_whole()
        all_menus_whole = MenuFullListOutSchema(menus=result)
        await self.cache.set_data_to_cache(
            key='all_menus_whole',
            value=all_menus_whole,
            background_tasks=self.background_tasks,
        )
        return all_menus_whole
