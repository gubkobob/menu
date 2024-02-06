import redis
from fastapi import Depends
from project.database import get_redis_client
from project.menus.schemas import MenuInSchema
from project.services_overal import RedisCache

from .repository import SubmenuRepository
from .schemas import SubMenuOutSchema


class SubmenuService:
    def __init__(
        self,
        submenu_repository: SubmenuRepository = Depends(),
        redis_client: redis.Redis = Depends(get_redis_client),
    ):
        self.submenu_repository = submenu_repository
        self.cache = RedisCache(redis_client)

    async def read_submenu(
        self, target_menu_id: str, target_submenu_id: str
    ) -> SubMenuOutSchema:
        key_submenu = '/'.join([target_menu_id, target_submenu_id])
        data = self.cache.get_data_from_cache(key=key_submenu)
        if data is not None:
            return data
        result = await self.submenu_repository.read_submenu(
            target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
        )
        self.cache.set_data_to_cache(key=key_submenu, value=result)
        return result

    async def read_submenus(self, target_menu_id: str) -> list[SubMenuOutSchema]:
        key_submenus = '/'.join([target_menu_id, 'submenus'])
        data = self.cache.get_data_from_cache(key=key_submenus)
        if data is not None:
            return data
        submenus = await self.submenu_repository.read_submenus(
            target_menu_id=target_menu_id
        )
        self.cache.set_data_to_cache(key=key_submenus, value=submenus)
        return submenus

    async def create_submenu(
        self, target_menu_id: str, submenu: MenuInSchema
    ) -> SubMenuOutSchema:
        inserted_submenu = await self.submenu_repository.create_submenu(
            target_menu_id=target_menu_id, submenu=submenu
        )
        key_submenus = '/'.join([target_menu_id, 'submenus'])
        self.cache.delete_data_from_cache('all_menus', target_menu_id, key_submenus)

        return inserted_submenu

    async def del_submenu(self, target_menu_id: str, target_submenu_id: str) -> dict[str, str | bool]:
        result = await self.submenu_repository.del_submenu(
            target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
        )
        key_submenus = '/'.join([target_menu_id, 'submenus'])
        key_submenu = '/'.join([target_menu_id, target_submenu_id])
        self.cache.delete_data_from_cache(
            'all_menus', target_menu_id, key_submenu, key_submenus
        )
        self.cache.clear_namespace_from_cache(key_submenu)
        return result

    async def update_submenu(
        self,
        target_menu_id: str,
        target_submenu_id: str,
        submenu: MenuInSchema,
    ) -> SubMenuOutSchema:
        changed_submenu = await self.submenu_repository.update_submenu(
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            submenu=submenu,
        )
        key_submenu = '/'.join([target_menu_id, target_submenu_id])
        key_submenus = '/'.join([target_menu_id, 'submenus'])
        self.cache.delete_data_from_cache(key_submenu, key_submenus)
        return changed_submenu
