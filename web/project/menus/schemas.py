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
    Базовая Pydantic-схема пользователя

    Parameters
    ----------
    api_key: str
        api_key пользователя
    name: str
        Имя пользователя
    password: str, optional
        Пароль аккаунта пользователя
    """

    title: str
    description: str


class MenuInSchema(BaseMenu):
    """
    Pydantic-схема пользователя для ввода данных
    """

    ...


class MenuOutSchema(BaseMenu):
    """
    Pydantic-схема для вывода данных о пользователе

    Parameters
    ----------
    id: int
        Идентификатор пользователя в СУБД
    """

    id: str

    class Config:
        orm_mode = True





