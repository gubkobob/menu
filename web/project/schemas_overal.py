"""
schemas.py
----------
Модуль реализует pydantic-схемы для валидации данных
 и обмена данных между сервисами.

"""

from pydantic import BaseModel


class NotFoundSchema(BaseModel):
    """
    Pydantic-схема результата запроса не найдено

    Parameters
    ----------

    detail: str
        детали ответа

    """

    detail: str

    class Config:
        orm_mode = True


class CorrectDeleteSchema(BaseModel):
    """
    Pydantic-схема ответа об удалении

    Parameters
    ----------
    result: bool
        Флаг успешного выполнения операции
    message: str
        сообщение
    """

    result: bool = True
    message: str

    class Config:
        orm_mode = True
