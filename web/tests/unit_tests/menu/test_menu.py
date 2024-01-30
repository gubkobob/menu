from sqlalchemy import select

from httpx import AsyncClient
import os

from project.database import async_session
from project.models import Menu


async def test_get_menus_handler_not_empty(create_menu, ac: AsyncClient):
    response = await ac.get("api/v1/menus/")
    assert response.status_code == 200
    assert response.json() != []


async def test_get_menus_handler_empty(ac: AsyncClient):
    response = await ac.get("api/v1/menus/")
    assert response.status_code == 200
    assert response.json() == []


async def test_post_menu_handler(ac: AsyncClient):
    response = await ac.post(
        "api/v1/menus/",
        json={"title": "My menu 3", "description": "My menu description 3"},
    )
    inserted_menu_id = response.json()["id"]
    assert response.status_code == 201
    assert response.json()["title"] == "My menu 3"
    assert response.json()["description"] == "My menu description 3"
    assert response.json()["id"] == inserted_menu_id

    async with async_session() as session:
        q = await session.execute(select(Menu).where(Menu.id == inserted_menu_id))
    menu = q.scalars().one_or_none()

    assert response.json()["title"] == menu.title
    assert response.json()["description"] == menu.description
    assert response.json()["id"] == menu.id


async def test_get_menu_handler(create_menu, ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{os.getenv('target_menu_id')}")
    assert response.status_code == 200
    assert response.json()["title"] == os.getenv("target_menu_title")
    assert response.json()["description"] == os.getenv("target_menu_description")
    assert response.json()["id"] == os.getenv("target_menu_id")


async def test_get_menu_handler_no_menu(ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{os.getenv('target_menu_id')}")
    assert response.status_code == 404
    assert response.json()["detail"] == "menu not found"


async def test_patch_menu_handler(create_menu, ac: AsyncClient):
    response = await ac.patch(
        f"api/v1/menus/{os.getenv('target_menu_id')}",
        json={
            "title": "My updated menu 1",
            "description": "My updated menu description 1",
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "My updated menu 1"
    assert response.json()["description"] == "My updated menu description 1"
    assert response.json()["id"] == os.getenv("target_menu_id")
    async with async_session() as session:
        q = await session.execute(
            select(Menu).where(Menu.id == os.getenv("target_menu_id"))
        )
    menu = q.scalars().one_or_none()

    assert response.json()["title"] == menu.title
    assert response.json()["description"] == menu.description
    assert response.json()["id"] == menu.id


async def test_patch_menu_handler_no_menu(ac: AsyncClient):
    response = await ac.patch(
        f"api/v1/menus/{os.getenv('target_menu_id')}",
        json={
            "title": "My updated menu 1",
            "description": "My updated menu description 1",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "menu not found"


async def test_delete_menu_handler(create_menu, ac: AsyncClient):
    response = await ac.delete(f"api/v1/menus/{os.getenv('target_menu_id')}")
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert response.json()["message"] == "The menu has been deleted"


async def test_delete_menu_handler_no_id(ac: AsyncClient):
    response = await ac.delete(f"api/v1/menus/{os.getenv('target_menu_id')}")
    assert response.status_code == 404
    assert response.json()["detail"] == "menu not found"
