import os

from httpx import AsyncClient


class TestIntegrationWholeSchema:
    async def test_post_menu_handler_success(self, ac: AsyncClient, reverse):
        response = await ac.post(
            reverse('post_menus'),
            json={'title': 'My menu 1', 'description': 'My menu description 1'},
        )
        inserted_menu_id = response.json()['id']
        os.environ['target_menu_id'] = inserted_menu_id
        assert response.status_code == 201
        assert response.json()['id'] == os.getenv('target_menu_id')

    async def test_post_submenu_handler_success(self, ac: AsyncClient, reverse):
        response = await ac.post(
            reverse(
                'post_submenus', target_menu_id=os.getenv('target_menu_id')
            ),
            json={'title': 'My submenu 1', 'description': 'My submenu description 1'},
        )

        inserted_submenu_id = response.json()['id']
        os.environ['target_submenu_id'] = inserted_submenu_id
        assert response.status_code == 201
        assert response.json()['id'] == os.getenv('target_submenu_id')

    async def test_post_dish_1_handler_success(self, ac: AsyncClient, reverse):
        response = await ac.post(
            reverse(
                'post_dishes',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            ),
            json={
                'title': 'My dish 2',
                'description': 'My dish description 2',
                'price': '13.50',
            },
        )
        inserted_dish_id = response.json()['id']
        os.environ['target_dish_id'] = inserted_dish_id
        assert response.status_code == 201
        assert response.json()['id'] == os.getenv('target_dish_id')

    async def test_post_dish_2_handler_success(self, ac: AsyncClient, reverse):
        response = await ac.post(
            reverse(
                'post_dishes',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            ),
            json={
                'title': 'My dish 1',
                'description': 'My dish description 1',
                'price': '12.50',
            },
        )
        inserted_dish_id = response.json()['id']
        os.environ['target_dish_id'] = inserted_dish_id
        assert response.status_code == 201
        assert response.json()['id'] == os.getenv('target_dish_id')

    async def test_get_menu_handler_success_with_count_dishes_and_submenus(
            self, ac: AsyncClient, reverse):
        response = await ac.get(
            reverse(
                'get_menu', target_menu_id=os.getenv('target_menu_id')
            )
        )
        assert response.status_code == 200
        assert response.json()['submenus_count'] == 1
        assert response.json()['dishes_count'] == 2
        assert response.json()['id'] == os.getenv('target_menu_id')

    async def test_get_submenu_handler_success_with_count_dishes(self, ac: AsyncClient, reverse):
        response = await ac.get(
            reverse(
                'get_submenu',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            )
        )
        assert response.status_code == 200
        assert response.json()['dishes_count'] == 2

    async def test_delete_submenu_handler_success(self, ac: AsyncClient, reverse):
        response = await ac.delete(
            reverse(
                'delete_submenu',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            )
        )
        assert response.status_code == 200

    async def test_get_submenus_handler_empty_list(self, ac: AsyncClient, reverse):
        response = await ac.get(
            reverse(
                'get_submenus', target_menu_id=os.getenv('target_menu_id')
            )
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_dishes_handler_empty_list(self, ac: AsyncClient, reverse):
        response = await ac.get(
            reverse(
                'get_dishes',
                target_menu_id=os.getenv('target_menu_id'),
                target_submenu_id=os.getenv('target_submenu_id'),
            )
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_menu_handler_success_after_delete_submenu(self, ac: AsyncClient, reverse):
        response = await ac.get(
            reverse(
                'get_menu', target_menu_id=os.getenv('target_menu_id')
            )
        )
        assert response.status_code == 200
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0
        assert response.json()['id'] == os.getenv('target_menu_id')

    async def test_delete_menu_handler_success(self, ac: AsyncClient, reverse):
        response = await ac.delete(
            reverse(
                'delete_menu', target_menu_id=os.getenv('target_menu_id')
            )
        )
        assert response.status_code == 200

    async def test_get_menus_handler_empty_list_after_delete(self, ac: AsyncClient, reverse):
        response = await ac.get(reverse('get_menus'))
        assert response.status_code == 200
        assert response.json() == []
