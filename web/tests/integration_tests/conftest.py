from typing import Callable

import pytest


@pytest.fixture(autouse=True)
async def prepare_for_integration_tests(
    prepare_database_for_integration_tests: Callable,
) -> None:
    pass
