"""
routes.py
----------
Модуль реализует эндпоинты FastApi для взамодействия с меню верхнего уровня.

"""
from typing import Union

from fastapi import APIRouter, Depends
from project.schemas_overal import CorrectDeleteSchema, NotFoundSchema

from .schemas import MenuFullListOutSchema, MenuInSchema, MenuOutSchema
from .services import MenuService

router = APIRouter(prefix='/menus', tags=['Menus'])


@router.get(
    '/{target_menu_id}',
    summary='Получение меню по id',
    response_description='Данные меню',
    response_model=Union[MenuOutSchema, NotFoundSchema],
    status_code=200,
)
async def get_menu_handler(
    target_menu_id: str,
    response: MenuService = Depends(),
) -> MenuOutSchema:
    """
    Эндпоинт возвращает меню по идентификатору или сообщение об ошибке
    \f
    :param target_menu_id: str
        Идентификатор меню в БД
    :param response: MenuService
         Обьект ответа на запрос из сервиса меню

    :return: Union[MenuOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с меню или ошибкой
    """

    return await response.read_menu(target_menu_id=target_menu_id)


@router.get(
    '',
    summary='Получение всех меню',
    response_description='список меню',
    response_model=list[MenuOutSchema],
    status_code=200,
)
async def get_menus_handler(
    response: MenuService = Depends(),
) -> list[MenuOutSchema]:
    """
    Эндпоинт возвращает все меню
    \f
    :param response: MenuService
         Обьект ответа на запрос из сервиса меню

    :return: List[MenuOutSchema]
        Pydantic-схема для фронтенда с меню
    """

    return await response.read_menus()


@router.post(
    '',
    summary='Публикация меню',
    response_description='Данные меню',
    response_model=MenuOutSchema,
    status_code=201,
)
async def post_menus_handler(
    menu: MenuInSchema,
    response: MenuService = Depends(),
) -> MenuOutSchema:
    """
    Эндпоинт публикации меню
    \f
    :param menu: MenuInSchema
        данные меню из pedantic-схемы ввода данных
    :param response: MenuService
         Обьект ответа на запрос из сервиса меню

    :return: MenuOutSchema
        Pydantic-схема для фронтенда с меню
    """
    return await response.create_menu(menu=menu)


@router.patch(
    '/{target_menu_id}',
    summary='Изменение меню',
    response_description='Данные меню',
    response_model=Union[MenuOutSchema, NotFoundSchema],
    status_code=200,
)
async def patch_menu_handler(
    target_menu_id: str,
    menu: MenuInSchema,
    response: MenuService = Depends(),
) -> MenuOutSchema:
    """
    Эндпоинт изменения меню
    \f
    :param target_menu_id: str
        Идентификатор меню в СУБД
    :param menu: MenuInSchema
        данные меню из pedantic-схемы ввода данных
    :param response: MenuService
         Обьект ответа на запрос из сервиса меню

    :return: Union[MenuOutSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с меню или ошибкой
    """

    return await response.update_menu(target_menu_id=target_menu_id, menu=menu)


@router.delete(
    '/{target_menu_id}',
    summary='Удаление меню',
    response_description='Сообщение о результате',
    response_model=Union[CorrectDeleteSchema, NotFoundSchema],
    status_code=200,
)
async def delete_menu_handler(
    target_menu_id: str,
    response: MenuService = Depends(),
) -> dict[str, bool | str]:
    """
    Эндпоинт удаления меню по его id
    \f
    :param target_menu_id: str
        Идентификатор меню в СУБД
    :param response: MenuService
         Обьект ответа на запрос из сервиса меню

    :return: Union[CorrectDeleteSchema, NotFoundSchema]
        Pydantic-схема для фронтенда с флагом об удачной операции или ошибкой
    """

    return await response.del_menu(target_menu_id=target_menu_id)


@router.get(
    '/whole/',
    summary='Получение всех меню с подменю и блюдами',
    response_description='список меню с подменю и блюдами',
    response_model=MenuFullListOutSchema,
    status_code=200,
)
async def get_menus_whole_handler(
    response: MenuService = Depends(),
) -> MenuFullListOutSchema:
    """
    Эндпоинт возвращает все меню с подменю и блюдами
    \f
    :param response: MenuService
         Обьект ответа на запрос из сервиса меню

    :return: MenuFullListOutSchema
        Pydantic-схема для фронтенда с меню с подменю и блюдами
    """
    return await response.read_menus_whole()
