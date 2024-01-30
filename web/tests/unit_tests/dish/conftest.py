import pytest


@pytest.fixture(autouse=True)
async def prepare_for_dishes_tests(prepare_database, create_menu, create_submenu):
    pass
