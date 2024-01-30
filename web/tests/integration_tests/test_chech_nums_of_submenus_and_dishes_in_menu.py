import os

from httpx import AsyncClient


async def test_post_menu_handler(ac: AsyncClient):
    response = await ac.post(
        "api/v1/menus/",
        json={"title": "My menu 1", "description": "My menu description 1"},
    )
    inserted_menu_id = response.json()["id"]
    os.environ["target_menu_id"] = inserted_menu_id
    assert response.status_code == 201
    assert response.json()["id"] == os.getenv("target_menu_id")


async def test_post_submenu_handler(ac: AsyncClient):
    response = await ac.post(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/",
        json={"title": "My submenu 1", "description": "My submenu description 1"},
    )

    inserted_submenu_id = response.json()["id"]
    os.environ["target_submenu_id"] = inserted_submenu_id
    assert response.status_code == 201
    assert response.json()["id"] == os.getenv("target_submenu_id")


async def test_post_dish_1_handler(ac: AsyncClient):
    response = await ac.post(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/",
        json={
            "title": "My dish 2",
            "description": "My dish description 2",
            "price": "13.50",
        },
    )
    inserted_dish_id = response.json()["id"]
    os.environ["target_dish_id"] = inserted_dish_id
    assert response.status_code == 201
    assert response.json()["id"] == os.getenv("target_dish_id")


async def test_post_dish_2_handler(ac: AsyncClient):
    response = await ac.post(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/",
        json={
            "title": "My dish 1",
            "description": "My dish description 1",
            "price": "12.50",
        },
    )
    inserted_dish_id = response.json()["id"]
    os.environ["target_dish_id"] = inserted_dish_id
    assert response.status_code == 201
    assert response.json()["id"] == os.getenv("target_dish_id")


async def test_get_menu_handler(ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{os.getenv('target_menu_id')}")
    assert response.status_code == 200
    assert response.json()["submenus_count"] == 1
    assert response.json()["dishes_count"] == 2
    assert response.json()["id"] == os.getenv("target_menu_id")


async def test_get_submenu_handler(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}"
    )
    assert response.status_code == 200
    assert response.json()["dishes_count"] == 2


async def test_delete_submenu_handler(ac: AsyncClient):
    response = await ac.delete(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}"
    )
    assert response.status_code == 200


async def test_get_submenus_handler(ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_dishes_handler(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/"
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_get_menu_handler_after_delete_submenu(ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{os.getenv('target_menu_id')}")
    assert response.status_code == 200
    assert response.json()["submenus_count"] == 0
    assert response.json()["dishes_count"] == 0
    assert response.json()["id"] == os.getenv("target_menu_id")


async def test_delete_menu_handler(ac: AsyncClient):
    response = await ac.delete(f"api/v1/menus/{os.getenv('target_menu_id')}")
    assert response.status_code == 200


async def test_get_menus_handler_after_delete(ac: AsyncClient):
    response = await ac.get("api/v1/menus/")
    assert response.status_code == 200
    assert response.json() == []
