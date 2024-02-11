import pickle
from typing import Any

import redis.asyncio as redis
from fastapi import BackgroundTasks, Depends

from .database import get_async_redis_client


class AsyncRedisCache:
    def __init__(self, redis_client: redis.Redis = Depends(get_async_redis_client())) -> None:
        self.redis_client = redis_client

    async def get_data_from_cache(self, key: str) -> Any | None:
        """берет данные из кеша"""
        result = await self.redis_client.get(key)
        if not result:
            return None
        val = pickle.loads(result)
        return val

    async def set_data_to_cache(
        self, key: str, value: Any, background_tasks: BackgroundTasks
    ) -> None:
        """добавляет данные в кеш"""

        val_bytes = pickle.dumps(value)
        background_tasks.add_task(self._set_cache, key, val_bytes)

    async def _set_cache(self, key: str, data: Any) -> None:
        await self.redis_client.set(key, data)

    async def delete_data_from_cache(
        self, *keys: str, background_tasks: BackgroundTasks
    ) -> None:
        """удаляет данные из кеша"""
        background_tasks.add_task(self._delete_cache, *keys)

    async def _delete_cache(self, *keys: str) -> None:
        await self.redis_client.delete(*keys)

    async def clear_namespace_from_cache(
        self, namespace: str, background_tasks: BackgroundTasks
    ) -> None:
        """удаляет данные из кеша с ключами, начинающимися на namespace"""
        background_tasks.add_task(self._clear_namespace_cache, namespace)

    async def _clear_namespace_cache(self, namespace: str) -> None:
        ns_keys = namespace + '*'
        async for key in self.redis_client.scan_iter(ns_keys):
            await self.redis_client.delete(key)
