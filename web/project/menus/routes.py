"""
routes.py
----------
Модуль реализует эндпоинты FastApi для взамодействия с меню верхнего уровня.

"""
from typing import Sequence, Union

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..exeptions import NotFoundException
from ..menus.schemas import MenuInSchema, MenuOutSchema
from ..menus.services import change_menu, delete_menu, get_menu, get_menus, post_menu
from ..models import Menu
from ..schemas_overal import CorrectDeleteSchema, NotFoundSchema

router = APIRouter(prefix='/menus', tags=['Menus'])


@router.get(
    '/{target_menu_id}',
    summary='Получение меню по id',
    response_description='Сообщение о результате',
    response_model=Union[MenuOutSchema, NotFoundSchema],
    status_code=200,
)
async def get_menu_handler(
    response: Response,
    target_menu_id: str,
    session: AsyncSession = Depends(get_session),
) -> Menu | dict[str, str]:
    """
    Эндпоинт возвращает меню по идентификатору или сообщение об ошибке
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в БД
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[MenuOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с меню или ошибкой
    """
    try:
        result = await get_menu(session=session, target_menu_id=target_menu_id)
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
    return result


@router.get(
    '',
    summary='Получение всех меню',
    response_description='список меню',
    response_model=list[MenuOutSchema],
    status_code=200,
)
async def get_menus_handler(
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> Sequence[Menu]:
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
    '',
    summary='Публикация меню',
    response_description='Сообщение о результате',
    response_model=Union[MenuOutSchema, dict],
    status_code=201,
)
async def post_menus_handler(
    response: Response,
    menu: MenuInSchema,
    session: AsyncSession = Depends(get_session),
) -> Menu | Exception:
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
    try:
        new_menu = await post_menu(
            session=session, title=menu.title, description=menu.description
        )
    except Exception as e:
        return e
    return new_menu


@router.patch(
    '/{target_menu_id}',
    summary='Изменение меню',
    response_description='Сообщение о результате',
    response_model=Union[MenuOutSchema, NotFoundSchema],
    status_code=200,
)
async def patch_menu_handler(
    response: Response,
    target_menu_id: str,
    menu: MenuInSchema,
    session: AsyncSession = Depends(get_session),
) -> Menu | dict[str, str]:
    """
    Эндпоинт изменения меню
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в СУБД
    :param menu: MenuInSchema
        данные меню из pedantic-схемы ввода данных
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[MenuOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с меню или ошибкой
    """

    try:
        changed_menu = await change_menu(
            session=session,
            target_menu_id=target_menu_id,
            title=menu.title,
            description=menu.description,
        )
        return changed_menu
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
        return result


@router.delete(
    '/{target_menu_id}',
    summary='Удаление меню',
    response_description='Сообщение о результате',
    response_model=Union[CorrectDeleteSchema, NotFoundSchema],
    status_code=200,
)
async def delete_menu_handler(
    response: Response,
    target_menu_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool | str]:
    """
    Эндпоинт удаления меню по его id
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в СУБД
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[CorrectDeleteSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с флагом об удачной операции или ошибкой
    """
    try:
        await delete_menu(session=session, target_menu_id=target_menu_id)
        return {'status': True, 'message': 'The menu has been deleted'}
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
        return result
