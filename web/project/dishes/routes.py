"""
routes.py
----------
Модуль реализует эндпоинты FastApi для взамодействия с блюдами.

"""

from typing import Union

from fastapi import APIRouter, Depends
from project.schemas_overal import CorrectDeleteSchema, NotFoundSchema

from .schemas import DishInSchema, DishOutSchema
from .services import DishService

router = APIRouter(
    prefix='/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
    tags=['Dishes'],
)


@router.get(
    '/{target_dish_id}',
    summary='Получение блюда по id',
    response_description='Данные блюда',
    response_model=Union[DishOutSchema, NotFoundSchema],
    status_code=200,
)
async def get_dish_handler(
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    response: DishService = Depends(),
) -> DishOutSchema | dict[str, str]:
    """
     Эндпоинт возвращает блюдо по идентификатору или сообщение об ошибке
     \f
     :param target_menu_id: str
         Идентификатор меню в БД
     :param target_submenu_id: str
         Идентификатор подменю в БД
     :param target_dish_id: str
         Идентификатор блюда в БД
    :param response: DishService
         Обьект ответа на запрос из сервиса блюд

     :return: Union[DishOutSchema, NotFoundSchema]
         Pydantic-схема для фронтенда с блюдом или ошибкой
    """

    return await response.read_dish(
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        target_dish_id=target_dish_id,
    )


@router.get(
    '',
    summary='Получение всех блюд',
    response_description='список блюд',
    response_model=list[DishOutSchema],
    status_code=200,
)
async def get_dishes_handler(
    target_menu_id: str,
    target_submenu_id: str,
    response: DishService = Depends(),
) -> list[DishOutSchema]:
    """
     Эндпоинт возвращает все блюда
     \f
     :param target_menu_id: str
         Идентификатор меню в БД
     :param target_submenu_id: str
         Идентификатор подменю в БД
    :param response: DishService
         Обьект ответа на запрос из сервиса блюд

     :return: List[DishOutSchema]
         Pydantic-схема для фронтенда с блюдами
    """
    return await response.read_dishes(
        target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
    )


@router.post(
    '',
    summary='Публикация блюда',
    response_description='Данные опубликованного блюда',
    response_model=DishOutSchema,
    status_code=201,
)
async def post_dishes_handler(
    target_menu_id: str,
    target_submenu_id: str,
    dish: DishInSchema,
    response: DishService = Depends(),
) -> DishOutSchema:
    """
     Эндпоинт публикации подменю
     \f
     :param target_menu_id: str
         Идентификатор меню в БД
     :param target_submenu_id: str
         Идентификатор подменю в БД
     :param dish: DishInSchema
         данные блюда из pedantic-схемы ввода данных
    :param response: DishService
         Обьект ответа на запрос из сервиса блюд

     :return: DishOutSchema
         Pydantic-схема для фронтенда с блюдом
    """
    return await response.create_dish(
        target_menu_id=target_menu_id, target_submenu_id=target_submenu_id, dish=dish
    )


@router.patch(
    '/{target_dish_id}',
    summary='Изменение блюда',
    response_description='Данные измененного блюда',
    response_model=Union[DishOutSchema, NotFoundSchema],
    status_code=200,
)
async def patch_dish_handler(
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    dish: DishInSchema,
    response: DishService = Depends(),
) -> DishOutSchema | dict[str, str]:
    """
     Эндпоинт изменения меню
     \f
     :param target_menu_id: str
         Идентификатор меню в СУБД
     :param target_submenu_id: str
         Идентификатор подменю в СУБД
     :param target_dish_id: str
         Идентификатор блюда в БД
     :param dish: DishInSchema
         данные блюда из pedantic-схемы ввода данных
    :param response: DishService
         Обьект ответа на запрос из сервиса блюд

     :return: Union[DishOutSchema, NotFoundSchema]
         Pydantic-схема для фронтенда с блюдом или ошибкой
    """

    return await response.update_dish(
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        target_dish_id=target_dish_id,
        dish=dish,
    )


@router.delete(
    '/{target_dish_id}',
    summary='Удаление блюда',
    response_description='Сообщение о результате',
    response_model=Union[CorrectDeleteSchema, NotFoundSchema],
    status_code=200,
)
async def delete_dish_handler(
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    response: DishService = Depends(),
) -> dict[str, bool | str]:
    """
     Эндпоинт удаления блюда по его id
     \f
     :param target_menu_id: str
         Идентификатор меню в СУБД
     :param target_submenu_id: str
         Идентификатор подменю в СУБД
     :param target_dish_id: str
         Идентификатор блюда в БД
    :param response: DishService
         Обьект ответа на запрос из сервиса блюд

     :return: Union[CorrectDeleteSchema, NotFoundSchema]
         Pydantic-схема для фронтенда с флагом об удачной операции или ошибкой
    """
    return await response.del_dish(
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        target_dish_id=target_dish_id,
    )
