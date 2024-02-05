"""
routes.py
----------
Модуль реализует эндпоинты FastApi для взамодействия с блюдами.

"""

from typing import Sequence, Union

from fastapi import APIRouter, Depends, Response
from project.database import get_db
from project.exeptions import NotFoundException
from project.models import Dish
from project.schemas_overal import CorrectDeleteSchema, NotFoundSchema
from sqlalchemy.ext.asyncio import AsyncSession

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
    db: AsyncSession = Depends(get_db),
) -> Dish | dict[str, str]:
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
   :param db: Asyncsession
        Экземпляр базы данных

    :return: Union[DishOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с блюдом или ошибкой
    """

    try:
        result = await get_dish(
            db=db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
    return result


@router.get(
    '',
    summary='Получение всех блюд',
    response_description='список блюд',
    response_model=list[DishOutSchema],
    status_code=200,
)
async def get_dishes_handler(
    response: Response,
    target_menu_id: str,
    target_submenu_id: str,
    db: AsyncSession = Depends(get_db),
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
   :param db: Asyncsession
        Экземпляр базы данных

    :return: List[DishOutSchema]
        Pydantic-схема для фронтенда с блюдами
    """
    try:
        result = await get_dishes(
            db=db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
        )
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
    return result


@router.post(
    '',
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
    db: AsyncSession = Depends(get_db),
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
   :param db: Asyncsession
        Экземпляр базы данных

    :return: Union[DishOutSchema, dict]
        Pydantic-схема для фронтенда с блюдом или ошибкой
    """
    try:
        new_dish = await post_dish(
            db=db,
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
    db: AsyncSession = Depends(get_db),
) -> Dish | dict[str, str]:
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
   :param db: Asyncsession
        Экземпляр базы данных

    :return: Union[DishOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с блюдом или ошибкой
    """

    try:
        changed_dish = await change_dish(
            db=db,
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
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool | str]:
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
   :param db: Asyncsession
        Экземпляр базы данных

    :return: Union[CorrectDeleteSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с флагом об удачной операции или ошибкой
    """
    try:
        await delete_dish(
            db=db,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        )
        return {'status': True, 'message': 'The dish has been deleted'}
    except NotFoundException as e:
        response.status_code = 404
        result = e.answer()
        return result
