"""
schemas.py
----------
Модуль реализует pydantic-схемы для валидации данных
 и обмена данных между сервисами.

"""

from project.dishes.schemas import DishOutSchema
from pydantic import BaseModel


class BaseSubMenu(BaseModel):
    """
    Базовая Pydantic-схема подменю

    Parameters
    ----------
    title: str
        Название подменю
    description: str
        Описание подменю
    """

    title: str
    description: str


class SubMenuOutSchema(BaseSubMenu):
    """
    Pydantic-схема для вывода данных о подменю

    Parameters
    ----------
    id: str
        Идентификатор подменю в СУБД
    dishes_count: int
        количество блюд в подменю
    """

    id: str
    dishes_count: int = 0

    class Config:
        orm_mode = True


class SubMenuFullOutSchema(BaseSubMenu):
    """
    Pydantic-схема для вывода данных о подменю c данными блюд

    Parameters
    ----------
    id: str
        Идентификатор подменю в СУБД
    dishes: list[DishOutSchema]
        список блюд
    """

    id: str
    dishes: list[DishOutSchema]

    class Config:
        orm_mode = True
