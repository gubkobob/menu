import asyncio
import os
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

from ..project.database import Base, async_session, engine, redis_client
from ..project.dishes.services import post_dish
from ..project.main import app
from ..project.menus.services import post_menu
from ..project.submenus.services import post_submenu


def reverse_path(route_name: str, **kwargs) -> str | None:
    routes = {
        'get_menu': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}',
        'get_menus': '/api/v1/menus/',
        'post_menus': '/api/v1/menus/',
        'patch_menu': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}',
        'delete_menu': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}',
        'get_submenu': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/{kwargs.get("target_submenu_id", "")}',
        'get_submenus': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/',
        'post_submenus': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/',
        'patch_submenu': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/{kwargs.get("target_submenu_id", "")}',
        'delete_submenu': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/{kwargs.get("target_submenu_id", "")}',
        'get_dish': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/'
                    f'{kwargs.get("target_submenu_id", "")}/dishes/{kwargs.get("target_dish_id", "")}',
        'get_dishes': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/{kwargs.get("target_submenu_id", "")}/dishes/',
        'post_dishes': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/{kwargs.get("target_submenu_id", "")}/dishes/',
        'patch_dish': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/'
                      f'{kwargs.get("target_submenu_id", "")}/dishes/{kwargs.get("target_dish_id", "")}',
        'delete_dish': f'/api/v1/menus/{kwargs.get("target_menu_id", "")}/submenus/'
                       f'{kwargs.get("target_submenu_id", "")}/dishes/{kwargs.get("target_dish_id", "")}',
    }

    return routes.get(route_name)


@pytest.fixture(scope='function', autouse=True)
def reverse():
    yield reverse_path


@pytest.fixture(scope='function')
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    redis_client.flushdb()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
async def prepare_database_for_integration_tests():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    redis_client.flushdb()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='function')
async def create_menu(monkeypatch):
    async with async_session() as session:
        menu = await post_menu(
            session=session, title='My menu 1', description='My menu description 1'
        )

    monkeypatch.setenv('target_menu_id', menu.id)
    monkeypatch.setenv('target_menu_title', menu.title)
    monkeypatch.setenv('target_menu_description', menu.description)


@pytest.fixture(scope='function')
async def create_submenu(create_menu, monkeypatch):
    async with async_session() as session:
        submenu = await post_submenu(
            session=session,
            target_menu_id=os.getenv('target_menu_id'),
            title='My submenu 1',
            description='My submenu description 1',
        )

    monkeypatch.setenv('target_submenu_id', submenu.id)
    monkeypatch.setenv('target_submenu_title', submenu.title)
    monkeypatch.setenv('target_submenu_description', submenu.description)


@pytest.fixture(scope='function')
async def create_dish(create_submenu, monkeypatch):
    async with async_session() as session:
        dish = await post_dish(
            session=session,
            target_menu_id=os.getenv('target_menu_id'),
            target_submenu_id=os.getenv('target_submenu_id'),
            title='My dish 1',
            description='My dish description 1',
            price='12.50',
        )

    monkeypatch.setenv('target_dish_id', dish.id)
    monkeypatch.setenv('target_dish_title', dish.title)
    monkeypatch.setenv('target_dish_description', dish.description)
    monkeypatch.setenv('target_dish_price', str(dish.price))
