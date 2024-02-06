from typing import Callable

import pytest


@pytest.fixture(autouse=True)
async def prepare_for_submenus_tests(
    prepare_database: Callable, create_menu: Callable
) -> None:
    pass
