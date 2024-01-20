"""
schemas.py
----------
Модуль реализует pydantic-схемы для валидации данных
 и обмена данных между сервисами.

"""

from typing import List, Optional

from pydantic import BaseModel, Field, validator
from pydantic.schema import Sequence
from sqlalchemy.ext.associationproxy import _AssociationList




class BaseMenu(BaseModel):
    """
    Базовая Pydantic-схема меню

    Parameters
    ----------
    title: str
        Название меню
    description: str
        Описание меню
    """

    title: str
    description: str


class MenuInSchema(BaseMenu):
    """
    Pydantic-схема меню для ввода данных
    """

    ...


class MenuOutSchema(BaseMenu):
    """
    Pydantic-схема для вывода данных о меню

    Parameters
    ----------
    id: str
        Идентификатор меню в СУБД
    submenus_count: int
        количество подменю в меню
    dishes_count: int
        количество блюд во всех подменю, входящих в меню
    """

    id: str
    submenus_count: int = 0
    dishes_count: int = 0

    class Config:
        orm_mode = True





