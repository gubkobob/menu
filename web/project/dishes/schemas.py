"""
schemas.py
----------
Модуль реализует pydantic-схемы для валидации данных
 и обмена данных между сервисами.

"""
import decimal

from ..menus.schemas import BaseMenu

class DishInSchema(BaseMenu):
    """
    Pydantic-схема меню для ввода данных блюда

    Parameters
    ----------
    price: float
        Цена блюда
    """

    price: str


class DishOutSchema(DishInSchema):
    """
    Pydantic-схема для вывода данных о блюде

    Parameters
    ----------
    id: str
        Идентификатор блюда в СУБД
    """

    id: str

    class Config:
        orm_mode = True





