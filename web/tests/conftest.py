import asyncio
import os
from asyncio import AbstractEventLoop
from collections.abc import AsyncIterator, Iterator
from typing import Any, AsyncGenerator, Callable

import pytest
import redis
from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient
from project.database import Base, async_session, engine, get_redis_client
from project.main import app
from project.models import Dish, Menu, Submenu
from sqlalchemy import insert, select


@pytest.fixture(scope='session')
def reverse() -> Callable:
    def reverse_path(route_name: str, **kwargs: dict[str, str]) -> str | None:
        routes = {
            'get_menu': app.url_path_for(
                'get_menu_handler', target_menu_id=kwargs.get('target_menu_id')
            ),
            'get_menus': app.url_path_for('get_menus_handler'),
            'post_menus': app.url_path_for('post_menus_handler'),
            'patch_menu': app.url_path_for(
                'patch_menu_handler', target_menu_id=kwargs.get('target_menu_id')
            ),
            'delete_menu': app.url_path_for(
                'delete_menu_handler', target_menu_id=kwargs.get('target_menu_id')
            ),
            'get_submenu': app.url_path_for(
                'get_submenu_handler',
                target_menu_id=kwargs.get('target_menu_id'),
                target_submenu_id=kwargs.get('target_submenu_id'),
            ),
            'get_submenus': app.url_path_for(
                'get_submenus_handler', target_menu_id=kwargs.get('target_menu_id')
            ),
            'post_submenus': app.url_path_for(
                'post_submenus_handler', target_menu_id=kwargs.get('target_menu_id')
            ),
            'patch_submenu': app.url_path_for(
                'patch_submenu_handler',
                target_menu_id=kwargs.get('target_menu_id'),
                target_submenu_id=kwargs.get('target_submenu_id'),
            ),
            'delete_submenu': app.url_path_for(
                'delete_submenu_handler',
                target_menu_id=kwargs.get('target_menu_id'),
                target_submenu_id=kwargs.get('target_submenu_id'),
            ),
            'get_dish': app.url_path_for(
                'get_dish_handler',
                target_menu_id=kwargs.get('target_menu_id'),
                target_submenu_id=kwargs.get('target_submenu_id'),
                target_dish_id=kwargs.get('target_dish_id'),
            ),
            'get_dishes': app.url_path_for(
                'get_dishes_handler',
                target_menu_id=kwargs.get('target_menu_id'),
                target_submenu_id=kwargs.get('target_submenu_id'),
            ),
            'post_dishes': app.url_path_for(
                'post_dishes_handler',
                target_menu_id=kwargs.get('target_menu_id'),
                target_submenu_id=kwargs.get('target_submenu_id'),
            ),
            'patch_dish': app.url_path_for(
                'patch_dish_handler',
                target_menu_id=kwargs.get('target_menu_id'),
                target_submenu_id=kwargs.get('target_submenu_id'),
                target_dish_id=kwargs.get('target_dish_id'),
            ),
            'delete_dish': app.url_path_for(
                'delete_dish_handler',
                target_menu_id=kwargs.get('target_menu_id'),
                target_submenu_id=kwargs.get('target_submenu_id'),
                target_dish_id=kwargs.get('target_dish_id'),
            ),
        }

        return routes.get(route_name)

    return reverse_path


@pytest.fixture(scope='function')
async def prepare_database(
    redis_client: redis.Redis = get_redis_client(),
) -> AsyncIterator:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    redis_client.flushdb()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
async def prepare_database_for_integration_tests(
    redis_client: redis.Redis = get_redis_client(),
) -> AsyncIterator:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    redis_client.flushdb()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request: Any) -> Iterator[AbstractEventLoop]:
    """Create an instance of the default event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='function')
async def create_menu(monkeypatch: MonkeyPatch) -> None:
    async with async_session() as session:
        insert_menu_query = await session.execute(
            insert(Menu).values(
                title='My menu 1',
                description='My menu description 1',
            )
        )
        new_menu_id = insert_menu_query.inserted_primary_key[0]
        await session.commit()
        q = await session.execute(select(Menu).where(Menu.id == new_menu_id))
        inserted_menu = q.scalars().one_or_none()

    monkeypatch.setenv('target_menu_id', inserted_menu.id)
    monkeypatch.setenv('target_menu_title', inserted_menu.title)
    monkeypatch.setenv('target_menu_description', inserted_menu.description)


@pytest.fixture(scope='function')
async def create_submenu(create_menu: Callable, monkeypatch: MonkeyPatch) -> None:
    async with async_session() as session:
        insert_submenu_query = await session.execute(
            insert(Submenu).values(
                title='My submenu 1',
                description='My submenu description 1',
                menu_id=os.getenv('target_menu_id'),
            )
        )
        new_submenu_id = insert_submenu_query.inserted_primary_key[0]
        await session.commit()
        q = await session.execute(select(Submenu).where(Submenu.id == new_submenu_id))
        inserted_submenu = q.scalars().one_or_none()

    monkeypatch.setenv('target_submenu_id', inserted_submenu.id)
    monkeypatch.setenv('target_submenu_title', inserted_submenu.title)
    monkeypatch.setenv('target_submenu_description', inserted_submenu.description)


@pytest.fixture(scope='function')
async def create_dish(create_submenu: Callable, monkeypatch: MonkeyPatch) -> None:
    async with async_session() as session:
        insert_dish_query = await session.execute(
            insert(Dish).values(
                title='My dish 1',
                description='My dish description 1',
                price='12.50',
                submenu_id=os.getenv('target_submenu_id'),
            )
        )
        new_dish_id = insert_dish_query.inserted_primary_key[0]
        await session.commit()
        q = await session.execute(select(Dish).where(Dish.id == new_dish_id))
        inserted_dish = q.scalars().one_or_none()

    monkeypatch.setenv('target_dish_id', inserted_dish.id)
    monkeypatch.setenv('target_dish_title', inserted_dish.title)
    monkeypatch.setenv('target_dish_description', inserted_dish.description)
    monkeypatch.setenv('target_dish_price', str(inserted_dish.price))
