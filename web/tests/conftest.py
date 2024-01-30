import asyncio
import os
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient


from ..project.config import settings
from ..project.database import Base, engine, async_session
from ..project.dishes.services import post_dish
from ..project.main import app
from ..project.menus.services import post_menu
from ..project.submenus.services import post_submenu


@pytest.fixture(scope="function")
async def prepare_database():
    print(settings.url_test)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def prepare_database_for_integration_tests():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def create_menu(monkeypatch):
    async with async_session() as session:
        menu = await post_menu(
            session=session, title="My menu 1", description="My menu description 1"
        )

    monkeypatch.setenv("target_menu_id", menu.id)
    monkeypatch.setenv("target_menu_title", menu.title)
    monkeypatch.setenv("target_menu_description", menu.description)


@pytest.fixture(scope="function")
async def create_submenu(create_menu, monkeypatch):
    async with async_session() as session:
        submenu = await post_submenu(
            session=session,
            target_menu_id=os.getenv("target_menu_id"),
            title="My submenu 1",
            description="My submenu description 1",
        )

    monkeypatch.setenv("target_submenu_id", submenu.id)
    monkeypatch.setenv("target_submenu_title", submenu.title)
    monkeypatch.setenv("target_submenu_description", submenu.description)


@pytest.fixture(scope="function")
async def create_dish(create_submenu, monkeypatch):
    async with async_session() as session:
        dish = await post_dish(
            session=session,
            target_menu_id=os.getenv("target_menu_id"),
            target_submenu_id=os.getenv("target_submenu_id"),
            title="My dish 1",
            description="My dish description 1",
            price="12.50",
        )

    monkeypatch.setenv("target_dish_id", dish.id)
    monkeypatch.setenv("target_dish_title", dish.title)
    monkeypatch.setenv("target_dish_description", dish.description)
    monkeypatch.setenv("target_dish_price", str(dish.price))
