import os

from httpx import AsyncClient
from project.database import async_session
from project.main import app
from project.models import Dish
from sqlalchemy import select


class TestDishes:
    async def test_get_dishes_handler_success(self, create_dish, ac: AsyncClient):
        response = await ac.get(
            app.url_path_for(
                'get_dishes_handler',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            )
        )
        assert response.status_code == 200
        assert response.json() != []

    async def test_get_dishes_handler_empty_list(self, ac: AsyncClient):
        response = await ac.get(
            app.url_path_for(
                'get_dishes_handler',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            )
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_post_dish_handler_success(self, ac: AsyncClient):
        response = await ac.post(
            app.url_path_for(
                'post_dishes_handler',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            ),
            json={
                'title': 'My dish 5',
                'description': 'My dish description 5',
                'price': '15.50343',
            },
        )
        inserted_dish_id = response.json()['id']
        assert response.status_code == 201
        assert response.json()['title'] == 'My dish 5'
        assert response.json()['description'] == 'My dish description 5'
        assert response.json()['price'] == '15.50'
        assert response.json()['id'] == inserted_dish_id

        async with async_session() as session:
            q = await session.execute(select(Dish).where(Dish.id == inserted_dish_id))
        dish = q.scalars().one_or_none()

        assert response.json()['title'] == dish.title
        assert response.json()['description'] == dish.description
        assert response.json()['id'] == dish.id
        assert response.json()['price'] == str(dish.price)

    async def test_get_dish_handler_success(self, create_dish, ac: AsyncClient):
        response = await ac.get(
            app.url_path_for(
                'get_dish_handler',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
                target_dish_id=os.getenv('target_dish_id'),
            )
        )
        assert response.status_code == 200
        assert response.json()['title'] == os.getenv('target_dish_title')
        assert response.json()['description'] == os.getenv('target_dish_description')
        assert response.json()['price'] == os.getenv('target_dish_price')
        assert response.json()['id'] == os.getenv('target_dish_id')

    async def test_get_dish_handler_not_found(self, ac: AsyncClient):
        response = await ac.get(
            app.url_path_for(
                'get_dish_handler',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
                target_dish_id=os.getenv('target_dish_id'),
            )
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'dish not found'

    async def test_patch_dish_handler_success(self, create_dish, ac: AsyncClient):
        response = await ac.patch(
            app.url_path_for(
                'patch_dish_handler',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
                target_dish_id=os.getenv('target_dish_id'),
            ),
            json={
                'title': 'My updated dish 1',
                'description': 'My updated dish description 1',
                'price': '14.50',
            },
        )
        assert response.status_code == 200
        assert response.json()['title'] == 'My updated dish 1'
        assert response.json()['description'] == 'My updated dish description 1'
        assert response.json()['price'] == '14.50'
        assert response.json()['id'] == os.getenv('target_dish_id')
        async with async_session() as session:
            q = await session.execute(
                select(Dish).where(Dish.id == os.getenv('target_dish_id'))
            )
        dish = q.scalars().one_or_none()

        assert response.json()['title'] == dish.title
        assert response.json()['description'] == dish.description
        assert response.json()['id'] == dish.id
        assert response.json()['price'] == str(dish.price)

    async def test_patch_dish_handler_not_found(self, ac: AsyncClient):
        response = await ac.patch(
            app.url_path_for(
                'patch_dish_handler',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
                target_dish_id=os.getenv('target_dish_id'),
            ),
            json={
                'title': 'My updated dish 1',
                'description': 'My updated dish description 1',
                'price': '14.50',
            },
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'dish not found'

    async def test_delete_dish_handler_success(self, create_dish, ac: AsyncClient):
        response = await ac.delete(
            app.url_path_for(
                'delete_dish_handler',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
                target_dish_id=os.getenv('target_dish_id'),
            )
        )
        assert response.status_code == 200
        assert response.json()['status'] is True
        assert response.json()['message'] == 'The dish has been deleted'

    async def test_delete_dish_handler_not_found(self, ac: AsyncClient):
        response = await ac.delete(
            app.url_path_for(
                'delete_dish_handler',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
                target_dish_id=os.getenv('target_dish_id'),
            )
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'dish not found'
