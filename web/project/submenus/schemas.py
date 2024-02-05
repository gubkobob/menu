"""
schemas.py
----------
Модуль реализует pydantic-схемы для валидации данных
 и обмена данных между сервисами.

"""
from project.menus.schemas import BaseMenu


class SubMenuOutSchema(BaseMenu):
    """
    Pydantic-схема для вывода данных о подменю

    Parameters
    ----------
    id: str
        Идентификатор пользователя в СУБД
    dishes_count: int
        количество блюд в подменю
    """

    id: str
    dishes_count: int = 0

    class Config:
        orm_mode = True
