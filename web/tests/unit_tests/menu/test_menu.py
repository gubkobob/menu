import os
from typing import Callable

from httpx import AsyncClient
from project.database import async_session
from project.models import Menu
from sqlalchemy import select


class TestMenus:
    async def test_get_menus_handler_not_empty(
        self, create_menu: Callable, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.get(reverse('get_menus'))
        assert response.status_code == 200
        assert response.json() != []

    async def test_get_menus_handler_empty_list(
        self, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.get(reverse('get_menus'))
        assert response.status_code == 200
        assert response.json() == []

    async def test_post_menu_handler_success(
        self, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.post(
            reverse('post_menus'),
            json={'title': 'My menu 3', 'description': 'My menu description 3'},
        )
        inserted_menu_id = response.json()['id']
        assert response.status_code == 201
        assert response.json()['title'] == 'My menu 3'
        assert response.json()['description'] == 'My menu description 3'
        assert response.json()['id'] == inserted_menu_id

        async with async_session() as session:
            q = await session.execute(select(Menu).where(Menu.id == inserted_menu_id))
        menu = q.scalars().one_or_none()

        assert response.json()['title'] == menu.title
        assert response.json()['description'] == menu.description
        assert response.json()['id'] == menu.id

    async def test_get_menu_handler_success(
        self, create_menu: Callable, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.get(
            reverse('get_menu', target_menu_id=os.getenv('target_menu_id'))
        )
        assert response.status_code == 200
        assert response.json()['title'] == os.getenv('target_menu_title')
        assert response.json()['description'] == os.getenv('target_menu_description')
        assert response.json()['id'] == os.getenv('target_menu_id')

    async def test_get_menu_handler_not_found_menu(
        self, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.get(
            reverse('get_menu', target_menu_id=os.getenv('target_menu_id'))
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'menu not found'

    async def test_patch_menu_handler_success(
        self, create_menu: Callable, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.patch(
            reverse('patch_menu', target_menu_id=os.getenv('target_menu_id')),
            json={
                'title': 'My updated menu 1',
                'description': 'My updated menu description 1',
            },
        )
        assert response.status_code == 200
        assert response.json()['title'] == 'My updated menu 1'
        assert response.json()['description'] == 'My updated menu description 1'
        assert response.json()['id'] == os.getenv('target_menu_id')
        async with async_session() as session:
            q = await session.execute(
                select(Menu).where(Menu.id == os.getenv('target_menu_id'))
            )
        menu = q.scalars().one_or_none()

        assert response.json()['title'] == menu.title
        assert response.json()['description'] == menu.description
        assert response.json()['id'] == menu.id

    async def test_patch_menu_handler_not_found_menu(
        self, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.patch(
            reverse('patch_menu', target_menu_id=os.getenv('target_menu_id')),
            json={
                'title': 'My updated menu 1',
                'description': 'My updated menu description 1',
            },
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'menu not found'

    async def test_delete_menu_handler_success(
        self, create_menu: Callable, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.delete(
            reverse('delete_menu', target_menu_id=os.getenv('target_menu_id'))
        )
        assert response.status_code == 200
        assert response.json()['status'] is True
        assert response.json()['message'] == 'The menu has been deleted'

    async def test_delete_menu_handler_not_found_menu(
        self, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.delete(
            reverse('delete_menu', target_menu_id=os.getenv('target_menu_id'))
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'menu not found'

    async def test_get_menus_whole_handler_empty_list(
        self, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.get(reverse('get_menus_whole'))
        assert response.status_code == 200
        assert response.json()['menus'] == []

    async def test_get_menus_whole_handler_not_empty_menus_empty_submenus(
        self, create_menu: Callable, ac: AsyncClient, reverse: Callable
    ) -> None:
        response = await ac.get(reverse('get_menus_whole'))
        assert response.status_code == 200
        assert response.json()['menus'] != []
        assert response.json()['menus'][0]['submenus'] == []

    async def test_get_menus_whole_handler_not_empty_menus_submenus_empty_dishes(
        self,
        create_menu: Callable,
        create_submenu: Callable,
        ac: AsyncClient,
        reverse: Callable,
    ) -> None:
        response = await ac.get(reverse('get_menus_whole'))
        assert response.status_code == 200
        assert response.json()['menus'] != []
        assert response.json()['menus'][0]['submenus'] != []
        assert response.json()['menus'][0]['submenus'][0]['dishes'] == []

    async def test_get_menus_whole_handler_not_empty_menus_submenus_dishes(
        self,
        create_menu: Callable,
        create_submenu: Callable,
        create_dish: Callable,
        ac: AsyncClient,
        reverse: Callable,
    ) -> None:
        response = await ac.get(reverse('get_menus_whole'))
        assert response.status_code == 200
        assert response.json()['menus'] != []
        assert response.json()['menus'][0]['submenus'] != []
        assert response.json()['menus'][0]['submenus'][0]['dishes'] != []
