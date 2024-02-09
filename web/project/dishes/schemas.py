"""
schemas.py
----------
Модуль реализует pydantic-схемы для валидации данных
 и обмена данных между сервисами.

"""

from pydantic import BaseModel


class BaseDish(BaseModel):
    """
    Базовая Pydantic-схема блюда

    Parameters
    ----------
    title: str
        Название блюда
    description: str
        Описание блюда
    price: str
        Цена блюда
    """

    title: str
    description: str
    price: str


class DishInSchema(BaseDish):
    """
    Pydantic-схема блюда для ввода данных
    """

    ...


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
