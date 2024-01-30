import pytest


@pytest.fixture(autouse=True)
async def prepare_for_submenus_tests(prepare_database, create_menu):
    pass
