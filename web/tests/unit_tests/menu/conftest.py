import pytest


@pytest.fixture(autouse=True)
async def prepare_for_menus_tests(prepare_database):
    pass
