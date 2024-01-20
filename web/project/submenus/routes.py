"""
routes.py
----------
Модуль реализует эндпоинты FastApi для взамодействия с меню верхнего уровня.

"""

from typing import Union, List, Any
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import SubMenuOutSchema
from .services import get_submenu, get_submenus, post_submenu, change_submenu, delete_submenu
from ..menus.schemas import MenuOutSchema, MenuInSchema
from ..menus.services import get_menu, get_menus, post_menu, delete_menu, change_menu

from ..database import get_session
from ..exeptions import NotFoundException
from ..schemas_overal import NotFoundSchema, CorrectDeleteSchema

router = APIRouter(prefix="/{target_menu_id}/submenus", tags=["SubMenus"])

@router.get(
    "/{target_submenu_id}",
    summary="Получение подменю по id",
    response_description="Сообщение о результате",
    response_model=Union[SubMenuOutSchema, NotFoundSchema],
    status_code=200,
)
async def get_menu_handler(
    response: Response, target_menu_id: str, target_submenu_id: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Эндпоинт возвращает подменю по идентификатору или сообщение об ошибке
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в БД
    :param target_submenu_id: str
        Идентификатор подменю в БД
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[SubMenuOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с подменю или ошибкой
    """

    try:
        result = await get_submenu(session=session, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id)
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
    return result


@router.get(
    "/",
    summary="Получение всех подменю",
    response_description="список подменю",
    response_model=Union[List[SubMenuOutSchema], NotFoundSchema],
    status_code=200,
)
async def get_submenus_handler(
    response: Response,
    target_menu_id: str,
    session: AsyncSession = Depends(get_session),
) -> list:
    """
    Эндпоинт возвращает все подменю
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в БД
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: List[SubMenuOutSchema]
        Pydantic-схема для фронтенда с подменю
    """
    try:
        result = await get_submenus(session=session, target_menu_id=target_menu_id)
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
    return result


@router.post(
    "/",
    summary="Публикация подменю",
    response_description="Сообщение о результате",
    response_model=Union[SubMenuOutSchema, dict],
    status_code=201,
)
async def post_menus_handler(
    response: Response,
    target_menu_id: str,
    submenu: MenuInSchema,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Эндпоинт публикации подменю
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в БД
    :param submenu: MenuInSchema
        данные подменю из pedantic-схемы ввода данных
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[SubMenuOutSchema, dict]
        Pydantic-схема для фронтенда с подменю или ошибкой
    """
    new_submenu = await post_submenu(
            session=session, target_menu_id=target_menu_id, title=submenu.title, description=submenu.description
        )

    return new_submenu


@router.patch(
    "/{target_submenu_id}",
    summary="Изменение подменю",
    response_description="Сообщение о результате",
    response_model=Union[SubMenuOutSchema, NotFoundSchema],
    status_code=200,
)
async def patch_menu_handler(
    response: Response,
    target_menu_id: str,
    target_submenu_id: str,
    submenu: MenuInSchema,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Эндпоинт изменения меню
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в СУБД
    :param target_submenu_id: str
        Идентификатор подменю в СУБД
    :param submenu: MenuInSchema
        данные подменю из pedantic-схемы ввода данных
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[SubMenuOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с меню или ошибкой
    """

    try:
        changed_submenu = await change_submenu(
            session=session, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id, title=submenu.title, description=submenu.description
        )
        return changed_submenu
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
        return result


@router.delete(
    "/{target_submenu_id}",
    summary="Удаление подменю",
    response_description="Сообщение о результате",
    response_model=Union[CorrectDeleteSchema, NotFoundSchema],
    status_code=200,
)
async def delete_submenu_handler(
    response: Response,
    target_menu_id: str,
    target_submenu_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Эндпоинт удаления подменю по его id
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в СУБД
    :param target_submenu_id: str
        Идентификатор подменю в СУБД
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[CorrectDeleteSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с флагом об удачной операции или ошибкой
    """
    try:
        await delete_submenu(session=session, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id)
        return {"status": True, "message": "The submenu has been deleted"}
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
        return result
