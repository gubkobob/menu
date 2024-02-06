from typing import Callable

import pytest


@pytest.fixture(autouse=True)
async def prepare_for_dishes_tests(
    prepare_database: Callable, create_menu: Callable, create_submenu: Callable
) -> None:
    pass
