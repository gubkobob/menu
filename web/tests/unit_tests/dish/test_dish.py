import os
from httpx import AsyncClient

from project.database import async_session
from sqlalchemy import select

from project.models import Dish


async def test_get_dishes_handler(create_dish, ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/"
    )
    assert response.status_code == 200
    assert response.json() != []


async def test_get_dishes_handler_no_dishes(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/"
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_post_dish_handler(ac: AsyncClient):
    response = await ac.post(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/",
        json={
            "title": "My dish 5",
            "description": "My dish description 5",
            "price": "15.50343",
        },
    )
    inserted_dish_id = response.json()["id"]
    assert response.status_code == 201
    assert response.json()["title"] == "My dish 5"
    assert response.json()["description"] == "My dish description 5"
    assert response.json()["price"] == "15.50"
    assert response.json()["id"] == inserted_dish_id

    async with async_session() as session:
        q = await session.execute(select(Dish).where(Dish.id == inserted_dish_id))
    dish = q.scalars().one_or_none()

    assert response.json()["title"] == dish.title
    assert response.json()["description"] == dish.description
    assert response.json()["id"] == dish.id
    assert response.json()["price"] == str(dish.price)


async def test_get_dish_handler(create_dish, ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/{os.getenv('target_dish_id')}"
    )
    assert response.status_code == 200
    assert response.json()["title"] == os.getenv("target_dish_title")
    assert response.json()["description"] == os.getenv("target_dish_description")
    assert response.json()["price"] == os.getenv("target_dish_price")
    assert response.json()["id"] == os.getenv("target_dish_id")


async def test_get_dish_handler_no_dish(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/{os.getenv('target_dish_id')}"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "dish not found"


async def test_patch_dish_handler(create_dish, ac: AsyncClient):
    response = await ac.patch(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/{os.getenv('target_dish_id')}",
        json={
            "title": "My updated dish 1",
            "description": "My updated dish description 1",
            "price": "14.50",
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "My updated dish 1"
    assert response.json()["description"] == "My updated dish description 1"
    assert response.json()["price"] == "14.50"
    assert response.json()["id"] == os.getenv("target_dish_id")
    async with async_session() as session:
        q = await session.execute(
            select(Dish).where(Dish.id == os.getenv("target_dish_id"))
        )
    dish = q.scalars().one_or_none()

    assert response.json()["title"] == dish.title
    assert response.json()["description"] == dish.description
    assert response.json()["id"] == dish.id
    assert response.json()["price"] == str(dish.price)


async def test_patch_dish_handler_no_dish(ac: AsyncClient):
    response = await ac.patch(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/{os.getenv('target_dish_id')}",
        json={
            "title": "My updated dish 1",
            "description": "My updated dish description 1",
            "price": "14.50",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "dish not found"


async def test_delete_dish_handler(create_dish, ac: AsyncClient):
    response = await ac.delete(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/{os.getenv('target_dish_id')}"
    )
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert response.json()["message"] == "The dish has been deleted"


async def test_delete_dish_handler_no_dish(ac: AsyncClient):
    response = await ac.delete(
        f"api/v1/menus/{os.getenv('target_menu_id')}/submenus/{os.getenv('target_submenu_id')}/dishes/{os.getenv('target_dish_id')}"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "dish not found"
