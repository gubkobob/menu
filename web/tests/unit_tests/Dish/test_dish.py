from httpx import AsyncClient

inserted_menu_id = ""
inserted_submenu_id = ""
inserted_dish_id = ""


async def test_post_menu_handler(ac: AsyncClient):
    response = await ac.post(
        "api/v1/menus/",
        json={"title": "My menu 1", "description": "My menu description 1"},
    )
    global inserted_menu_id
    inserted_menu_id = response.json()["id"]
    assert response.status_code == 201
    assert response.json()["title"] == "My menu 1"
    assert response.json()["description"] == "My menu description 1"
    assert response.json()["id"] == inserted_menu_id


async def test_post_submenu_handler(ac: AsyncClient):
    response = await ac.post(
        f"api/v1/menus/{inserted_menu_id}/submenus/",
        json={"title": "My submenu 1", "description": "My submenu description 1"},
    )
    global inserted_submenu_id
    inserted_submenu_id = response.json()["id"]
    assert response.status_code == 201
    assert response.json()["title"] == "My submenu 1"
    assert response.json()["description"] == "My submenu description 1"
    assert response.json()["id"] == inserted_submenu_id


async def test_get_dishes_handler(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}/dishes/"
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_post_dish_handler(ac: AsyncClient):
    response = await ac.post(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}/dishes/",
        json={
            "title": "My dish 1",
            "description": "My dish description 1",
            "price": "12.50",
        },
    )
    global inserted_dish_id
    inserted_dish_id = response.json()["id"]
    assert response.status_code == 201
    assert response.json()["title"] == "My dish 1"
    assert response.json()["description"] == "My dish description 1"
    assert response.json()["price"] == "12.50"
    assert response.json()["id"] == inserted_dish_id


async def test_get_dishes_handler_not_empty(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}/dishes/"
    )
    assert response.status_code == 200
    assert response.json() != []


async def test_get_dish_handler(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}/dishes/{inserted_dish_id}"
    )
    assert response.status_code == 200
    assert response.json()["title"] == "My dish 1"
    assert response.json()["description"] == "My dish description 1"
    assert response.json()["price"] == "12.50"
    assert response.json()["id"] == inserted_dish_id


async def test_patch_dish_handler(ac: AsyncClient):
    response = await ac.patch(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}/dishes/{inserted_dish_id}",
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
    assert response.json()["id"] == inserted_dish_id


async def test_get_dish_handler_after_patch(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}/dishes/{inserted_dish_id}"
    )
    assert response.status_code == 200
    assert response.json()["title"] == "My updated dish 1"
    assert response.json()["description"] == "My updated dish description 1"
    assert response.json()["price"] == "14.50"
    assert response.json()["id"] == inserted_dish_id


async def test_delete_dish_handler(ac: AsyncClient):
    response = await ac.delete(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}/dishes/{inserted_dish_id}"
    )
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert response.json()["message"] == "The dish has been deleted"


async def test_get_dishes_handler_2(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}/dishes/"
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_get_dish_handler_not_found(ac: AsyncClient):
    response = await ac.get(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}/dishes/{inserted_dish_id}"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "dish not found"


async def test_delete_submenu_handler(ac: AsyncClient):
    response = await ac.delete(
        f"api/v1/menus/{inserted_menu_id}/submenus/{inserted_submenu_id}"
    )
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert response.json()["message"] == "The submenu has been deleted"


async def test_get_submenus_handler(ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{inserted_menu_id}/submenus/")
    assert response.status_code == 200
    assert response.json() == []


async def test_delete_menu_handler(ac: AsyncClient):
    response = await ac.delete(f"api/v1/menus/{inserted_menu_id}")
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert response.json()["message"] == "The menu has been deleted"


async def test_get_menus_handler_after_delete(ac: AsyncClient):
    response = await ac.get("api/v1/menus/")
    assert response.status_code == 200
    assert response.json() == []
