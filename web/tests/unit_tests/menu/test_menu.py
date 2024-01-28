from httpx import AsyncClient

inserted_menu_id = ""


async def test_get_menus_handler(ac: AsyncClient):
    response = await ac.get("api/v1/menus/")
    assert response.status_code == 200
    assert response.json() == []


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


async def test_get_menu_handler(ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{inserted_menu_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "My menu 1"
    assert response.json()["description"] == "My menu description 1"
    assert response.json()["id"] == inserted_menu_id


async def test_get_menu_handler_bad_id(ac: AsyncClient):
    not_exist_id = "b9b2839f-ad5b-4eca-9ed4-48d3664049da"
    response = await ac.get(f"api/v1/menus/{not_exist_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "menu not found"


async def test_patch_menu_handler(ac: AsyncClient):
    response = await ac.patch(
        f"api/v1/menus/{inserted_menu_id}",
        json={
            "title": "My updated menu 1",
            "description": "My updated menu description 1",
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "My updated menu 1"
    assert response.json()["description"] == "My updated menu description 1"
    assert response.json()["id"] == inserted_menu_id


async def test_delete_menu_handler(ac: AsyncClient):
    response = await ac.delete(f"api/v1/menus/{inserted_menu_id}")
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert response.json()["message"] == "The menu has been deleted"


async def test_delete_menu_handler_no_id(ac: AsyncClient):
    not_exist_id = "b9b2839f-ad5b-4eca-9ed4-48d3664049da"
    response = await ac.delete(f"api/v1/menus/{not_exist_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "menu not found"


async def test_get_menu_handler_after_delete(ac: AsyncClient):
    response = await ac.get(f"api/v1/menus/{inserted_menu_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "menu not found"


async def test_get_menus_handler_after_delete(ac: AsyncClient):
    response = await ac.get("api/v1/menus/")
    assert response.status_code == 200
    assert response.json() == []
