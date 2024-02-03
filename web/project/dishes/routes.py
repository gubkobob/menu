"""
routes.py
----------
Модуль реализует эндпоинты FastApi для взамодействия с блюдами.

"""

from typing import Sequence, Union

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..exeptions import NotFoundException
from ..models import Dish
from ..schemas_overal import CorrectDeleteSchema, NotFoundSchema
from .schemas import DishInSchema, DishOutSchema
from .services import change_dish, delete_dish, get_dish, get_dishes, post_dish

router = APIRouter(
    prefix='/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
    tags=['Dishes'],
)


@router.get(
    '/{target_dish_id}',
    summary='Получение блюда по id',
    response_description='Сообщение о результате',
    response_model=Union[DishOutSchema, NotFoundSchema],
    status_code=200,
)
async def get_dish_handler(
    response: Response,
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    session: AsyncSession = Depends(get_session),
) -> Dish | dict:
    """
    Эндпоинт возвращает блюдо по идентификатору или сообщение об ошибке
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в БД
    :param target_submenu_id: str
        Идентификатор подменю в БД
    :param target_dish_id: str
        Идентификатор блюда в БД
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[DishOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с блюдом или ошибкой
    """

    try:
        result = await get_dish(
            session=session,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
    return result


@router.get(
    '/',
    summary='Получение всех блюд',
    response_description='список блюд',
    response_model=list[DishOutSchema],
    status_code=200,
)
async def get_dishes_handler(
    response: Response,
    target_menu_id: str,
    target_submenu_id: str,
    session: AsyncSession = Depends(get_session),
) -> Sequence[Dish]:
    """
    Эндпоинт возвращает все блюда
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в БД
    :param target_submenu_id: str
        Идентификатор подменю в БД
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: List[DishOutSchema]
        Pydantic-схема для фронтенда с блюдами
    """
    try:
        result = await get_dishes(
            session=session,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
        )
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
    return result


@router.post(
    '/',
    summary='Публикация блюда',
    response_description='Сообщение о результате',
    response_model=Union[DishOutSchema, dict],
    status_code=201,
)
async def post_dishes_handler(
    response: Response,
    target_menu_id: str,
    target_submenu_id: str,
    dish: DishInSchema,
    session: AsyncSession = Depends(get_session),
) -> Dish | Exception:
    """
    Эндпоинт публикации подменю
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в БД
    :param target_submenu_id: str
        Идентификатор подменю в БД
    :param dish: DishInSchema
        данные блюда из pedantic-схемы ввода данных
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[DishOutSchema, dict]
        Pydantic-схема для фронтенда с блюдом или ошибкой
    """
    try:
        new_dish = await post_dish(
            session=session,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            title=dish.title,
            description=dish.description,
            price=dish.price,
        )
    except Exception as e:
        return e

    return new_dish


@router.patch(
    '/{target_dish_id}',
    summary='Изменение блюда',
    response_description='Сообщение о результате',
    response_model=Union[DishOutSchema, NotFoundSchema],
    status_code=200,
)
async def patch_dish_handler(
    response: Response,
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    dish: DishInSchema,
    session: AsyncSession = Depends(get_session),
) -> Dish | dict:
    """
    Эндпоинт изменения меню
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в СУБД
    :param target_submenu_id: str
        Идентификатор подменю в СУБД
    :param target_dish_id: str
        Идентификатор блюда в БД
    :param dish: DishInSchema
        данные блюда из pedantic-схемы ввода данных
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[DishOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с блюдом или ошибкой
    """

    try:
        changed_dish = await change_dish(
            session=session,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
            title=dish.title,
            description=dish.description,
            price=dish.price,
        )
        return changed_dish
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
        return result


@router.delete(
    '/{target_dish_id}',
    summary='Удаление блюда',
    response_description='Сообщение о результате',
    response_model=Union[CorrectDeleteSchema, NotFoundSchema],
    status_code=200,
)
async def delete_dish_handler(
    response: Response,
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Эндпоинт удаления блюда по его id
    \f
    :param response: Response
         Обьект ответа на запрос
    :param target_menu_id: str
        Идентификатор меню в СУБД
    :param target_submenu_id: str
        Идентификатор подменю в СУБД
    :param target_dish_id: str
        Идентификатор блюда в БД
    :param session: Asyncsession
        Экземпляр сессии из sqlalchemy

    :return: Union[CorrectDeleteSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с флагом об удачной операции или ошибкой
    """
    try:
        await delete_dish(
            session=session,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )
        return {'status': True, 'message': 'The dish has been deleted'}
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
        return result
