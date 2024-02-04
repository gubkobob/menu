import pickle
from typing import Any

from .database import redis_client


def get_data_from_cache(key: str) -> Any | None:
    """берет данные из кеша"""
    result = redis_client.get(key)
    if not result:
        return result
    val = pickle.loads(result)
    return val


def set_data_to_cache(key: str, value: Any) -> bool | None:
    """добавляет данные в кеш"""

    val_bytes = pickle.dumps(value)
    result = redis_client.set(
        key,
        val_bytes,
    )
    return result


def delete_data_from_cache(*keys: str):
    """удаляет данные из кеша"""
    redis_client.delete(*keys)


def clear_namespace_from_cache(namespace: str) -> int:
    """удаляет данные из кеша с ключами, начинающимися на namespace"""
    count = 0
    ns_keys = namespace + '*'
    for key in redis_client.scan_iter(ns_keys):
        redis_client.delete(key)
        count += 1
    return count
