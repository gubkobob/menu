import pickle
from typing import Any

import redis
from fastapi import BackgroundTasks, Depends

from .database import get_redis_client


class RedisCache:
    def __init__(self, redis_client: redis.Redis = Depends(get_redis_client())) -> None:
        self.redis_client = redis_client

    def get_data_from_cache(self, key: str) -> Any | None:
        """берет данные из кеша"""
        result = self.redis_client.get(key)
        if not result:
            return None
        val = pickle.loads(result)
        return val

    def set_data_to_cache(self, key: str, value: Any, background_tasks: BackgroundTasks) -> None:
        """добавляет данные в кеш"""

        val_bytes = pickle.dumps(value)
        background_tasks.add_task(self._set_cache, key, val_bytes)

    def _set_cache(self, key: str, data: Any) -> None:
        self.redis_client.set(key, data)

    def delete_data_from_cache(self, *keys: str, background_tasks: BackgroundTasks) -> None:
        """удаляет данные из кеша"""
        background_tasks.add_task(self._delete_cache, *keys)

    def _delete_cache(self, *keys: str) -> None:
        self.redis_client.delete(*keys)

    def clear_namespace_from_cache(self, namespace: str, background_tasks: BackgroundTasks) -> None:
        """удаляет данные из кеша с ключами, начинающимися на namespace"""
        background_tasks.add_task(self._clear_namespace_cache, namespace)

    def _clear_namespace_cache(self, namespace: str) -> None:
        ns_keys = namespace + '*'
        for key in self.redis_client.scan_iter(ns_keys):
            self.redis_client.delete(key)
