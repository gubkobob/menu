"""
routes.py
----------
Модуль реализует эндпоинты FastApi для взамодействия с меню верхнего уровня.

"""

from typing import Union, List

from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..menus.schemas import MenuOutSchema, MenuInSchema
from ..menus.services import get_menu, get_menus, post_menu

from ..database import get_session
from ..exeptions import NotFoundException


router = APIRouter(prefix="", tags=["Menus"])

@router.get(
    "/{target_menu_id}",
    summary="Получение меню по id",
    response_description="Сообщение о результате",
    response_model=Union[MenuOutSchema, dict],
    status_code=200,
)
async def get_menu_handler(
    response: Response, target_menu_id: int, session: AsyncSession = Depends(get_session)
) -> Union[MenuOutSchema, dict]:
    """
    Эндпоинт возвращает меню по идентификатору или сообщение об ошибке
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: int
        Идентификатор меню в БД
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[MenuOutSchema, dict]
        Pydantic-схема для фронтенда с меню или ошибкой
    """

    try:
        result = await get_menu(session=session, target_menu_id=target_menu_id)
    except NotFoundException as e:
        response.status_code = 404
        result = e

    return result


@router.get(
    "/",
    summary="Получение всех меню",
    response_description="список меню",
    response_model=List[MenuOutSchema],
    status_code=200,
)
async def get_menus_handler(
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> List[MenuOutSchema]:
    """
    Эндпоинт возвращает все меню
    \f
    :param response: Response
         Обьект ответа на запрос
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: List[MenuOutSchema]
        Pydantic-схема для фронтенда с меню
    """

    result = await get_menus(session=session)
    return result


@router.post(
    "/",
    summary="Публикация меню",
    response_description="Сообщение о результате",
    response_model=Union[MenuOutSchema, dict],
    status_code=201,
)
async def post_menus_handler(
    response: Response,
    menu: MenuInSchema,
    session: AsyncSession = Depends(get_session),
) -> Union[MenuOutSchema, dict]:
    """
    Эндпоинт публикации меню
    \f
    :param response: Response
         Обьект ответа на запрос
    :param menu: MenuInSchema
        данные меню из pedantic-схемы ввода данных
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[MenuOutSchema, dict]
        Pydantic-схема для фронтенда с меню или ошибкой
    """
    new_menu = await post_menu(
            session=session, title=menu.title, description=menu.description
        )

    return new_menu
