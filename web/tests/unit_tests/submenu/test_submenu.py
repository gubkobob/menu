import os

from httpx import AsyncClient

from project.database import async_session
from sqlalchemy import select

from project.models import Submenu


async def test_get_submenus_handler(create_submenu, ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/")
    assert response.status_code == 200
    assert response.json() != []


async def test_get_submenus_handler_no_submenus(ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/")
    assert response.status_code == 200
    assert response.json() == []


async def test_post_submenu_handler(ac: AsyncClient):
    response = await ac.post(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/",
        json={"title": "My submenu 4", "description": "My submenu description 4"},
    )
    inserted_submenu_id = response.json()["id"]
    assert response.status_code == 201
    assert response.json()["title"] == "My submenu 4"
    assert response.json()["description"] == "My submenu description 4"
    assert response.json()["id"] == inserted_submenu_id

    async with async_session() as session:
        q = await session.execute(
            select(Submenu).where(Submenu.id == inserted_submenu_id)
        )
    submenu = q.scalars().one_or_none()

    assert response.json()["title"] == submenu.title
    assert response.json()["description"] == submenu.description
    assert response.json()["id"] == submenu.id


async def test_get_submenu_handler(create_submenu, ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}"
    )
    assert response.status_code == 200
    assert response.json()["title"] == os.getenv("target_submenu_title")
    assert response.json()["description"] == os.getenv("target_submenu_description")
    assert response.json()["id"] == os.getenv("target_submenu_id")


async def test_get_submenu_handler_no_submenu(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "submenu not found"


async def test_patch_submenu_handler(create_submenu, ac: AsyncClient):
    response = await ac.patch(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}",
        json={
            "title": "My updated submenu 1",
            "description": "My updated submenu description 1",
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "My updated submenu 1"
    assert response.json()["description"] == "My updated submenu description 1"
    assert response.json()["id"] == os.getenv("target_submenu_id")
    async with async_session() as session:
        q = await session.execute(
            select(Submenu).where(Submenu.id == os.getenv("target_submenu_id"))
        )
    submenu = q.scalars().one_or_none()

    assert response.json()["title"] == submenu.title
    assert response.json()["description"] == submenu.description
    assert response.json()["id"] == submenu.id


async def test_patch_submenu_handler_no_submenu(ac: AsyncClient):
    response = await ac.patch(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}",
        json={
            "title": "My updated submenu 1",
            "description": "My updated submenu description 1",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "submenu not found"


async def test_delete_submenu_handler(create_submenu, ac: AsyncClient):
    response = await ac.delete(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}"
    )
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert response.json()["message"] == "The submenu has been deleted"


async def test_delete_submenu_handler_no_id(ac: AsyncClient):
    response = await ac.delete(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "submenu not found"
