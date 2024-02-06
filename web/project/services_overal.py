import pickle
from typing import Any

import redis
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_redis_client
from .models import Dish, Menu, Submenu


async def validate_menu(db: AsyncSession, target_menu_id: str):
    res_q = await db.execute(select(Menu).where(Menu.id == target_menu_id))
    result = res_q.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail='menu not found')


async def validate_submenu(
    db: AsyncSession, target_menu_id: str, target_submenu_id: str
):
    await validate_menu(db=db, target_menu_id=target_menu_id)
    res_q = await db.execute(select(Submenu).where(Submenu.id == target_submenu_id))
    result = res_q.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail='submenu not found')


async def validate_dish(
    db: AsyncSession, target_menu_id: str, target_submenu_id: str, target_dish_id: str
):
    await validate_submenu(
        db=db, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
    )
    res_q = await db.execute(select(Dish).where(Dish.id == target_dish_id))
    result = res_q.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail='dish not found')


class RedisCache:
    def __init__(self, redis_client: redis.Redis = Depends(get_redis_client())) -> None:
        self.redis_client = redis_client

    def get_data_from_cache(self, key: str) -> Any | None:
        """берет данные из кеша"""
        result = self.redis_client.get(key)
        if not result:
            return result
        val = pickle.loads(result)
        return val

    def set_data_to_cache(self, key: str, value: Any) -> bool | None:
        """добавляет данные в кеш"""

        val_bytes = pickle.dumps(value)
        result = self.redis_client.set(
            key,
            val_bytes,
        )
        return result

    def delete_data_from_cache(self, *keys: str):
        """удаляет данные из кеша"""
        self.redis_client.delete(*keys)

    def clear_namespace_from_cache(self, namespace: str) -> int:
        """удаляет данные из кеша с ключами, начинающимися на namespace"""
        count = 0
        ns_keys = namespace + '*'
        for key in self.redis_client.scan_iter(ns_keys):
            self.redis_client.delete(key)
            count += 1
        return count
