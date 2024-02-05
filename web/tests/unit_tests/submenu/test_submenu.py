import os

from httpx import AsyncClient
from project.database import async_session
from project.models import Submenu
from sqlalchemy import select


class TestSubmenus:
    async def test_get_submenus_handler_success(
        self, create_submenu, ac: AsyncClient, reverse
    ):
        response = await ac.get(
            reverse('get_submenus', target_menu_id=os.getenv('target_menu_id'))
        )
        assert response.status_code == 200
        assert response.json() != []

    async def test_get_submenus_handler_empty_list(self, ac: AsyncClient, reverse):
        response = await ac.get(
            reverse('get_submenus', target_menu_id=os.getenv('target_menu_id'))
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_post_submenu_handler_success(self, ac: AsyncClient, reverse):
        response = await ac.post(
            reverse('post_submenus', target_menu_id=os.getenv('target_menu_id')),
            json={'title': 'My submenu 4', 'description': 'My submenu description 4'},
        )
        inserted_submenu_id = response.json()['id']
        assert response.status_code == 201
        assert response.json()['title'] == 'My submenu 4'
        assert response.json()['description'] == 'My submenu description 4'
        assert response.json()['id'] == inserted_submenu_id

        async with async_session() as session:
            q = await session.execute(
                select(Submenu).where(Submenu.id == inserted_submenu_id)
            )
        submenu = q.scalars().one_or_none()

        assert response.json()['title'] == submenu.title
        assert response.json()['description'] == submenu.description
        assert response.json()['id'] == submenu.id

    async def test_get_submenu_handler_success(
        self, create_submenu, ac: AsyncClient, reverse
    ):
        response = await ac.get(
            reverse(
                'get_submenu',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            )
        )
        assert response.status_code == 200
        assert response.json()['title'] == os.getenv('target_submenu_title')
        assert response.json()['description'] == os.getenv('target_submenu_description')
        assert response.json()['id'] == os.getenv('target_submenu_id')

    async def test_get_submenu_handler_not_found_submenu(
        self, ac: AsyncClient, reverse
    ):
        response = await ac.get(
            reverse(
                'get_submenu',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            )
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'submenu not found'

    async def test_patch_submenu_handler_success(
        self, create_submenu, ac: AsyncClient, reverse
    ):
        response = await ac.patch(
            reverse(
                'patch_submenu',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            ),
            json={
                'title': 'My updated submenu 1',
                'description': 'My updated submenu description 1',
            },
        )
        assert response.status_code == 200
        assert response.json()['title'] == 'My updated submenu 1'
        assert response.json()['description'] == 'My updated submenu description 1'
        assert response.json()['id'] == os.getenv('target_submenu_id')
        async with async_session() as session:
            q = await session.execute(
                select(Submenu).where(Submenu.id == os.getenv('target_submenu_id'))
            )
        submenu = q.scalars().one_or_none()

        assert response.json()['title'] == submenu.title
        assert response.json()['description'] == submenu.description
        assert response.json()['id'] == submenu.id

    async def test_patch_submenu_handler_submenu_not_found(
        self, ac: AsyncClient, reverse
    ):
        response = await ac.patch(
            reverse(
                'patch_submenu',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            ),
            json={
                'title': 'My updated submenu 1',
                'description': 'My updated submenu description 1',
            },
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'submenu not found'

    async def test_delete_submenu_handler_success(
        self, create_submenu, ac: AsyncClient, reverse
    ):
        response = await ac.delete(
            reverse(
                'delete_submenu',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            )
        )
        assert response.status_code == 200
        assert response.json()['status'] is True
        assert response.json()['message'] == 'The submenu has been deleted'

    async def test_delete_submenu_handler_not_found_submenu(
        self, ac: AsyncClient, reverse
    ):
        response = await ac.delete(
            reverse(
                'delete_submenu',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            )
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'submenu not found'
