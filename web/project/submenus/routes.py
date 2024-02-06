"""
routes.py
----------
Модуль реализует эндпоинты FastApi для взамодействия с подменю.

"""

from typing import Union

from fastapi import APIRouter, Depends
from project.menus.schemas import MenuInSchema
from project.schemas_overal import CorrectDeleteSchema, NotFoundSchema

from .schemas import SubMenuOutSchema
from .services import SubmenuService

router = APIRouter(prefix='/menus/{target_menu_id}/submenus', tags=['SubMenus'])


@router.get(
    '/{target_submenu_id}',
    summary='Получение подменю по id',
    response_description='Данные подменю',
    response_model=Union[SubMenuOutSchema, NotFoundSchema],
    status_code=200,
)
async def get_submenu_handler(
    target_menu_id: str,
    target_submenu_id: str,
    response: SubmenuService = Depends(),
) -> SubMenuOutSchema | dict[str, str]:
    """
     Эндпоинт возвращает подменю по идентификатору или сообщение об ошибке
     \f
     :param target_menu_id: str
         Идентификатор меню в БД
     :param target_submenu_id: str
         Идентификатор подменю в БД
    :param response: SubmenuService
         Обьект ответа на запрос из сервиса подменю

     :return: Union[SubMenuOutSchema, NotFoundSchema]
         Pydantic-схема для фронтенда с подменю или ошибкой
    """

    return await response.read_submenu(
        target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
    )


@router.get(
    '',
    summary='Получение всех подменю',
    response_description='список подменю',
    response_model=Union[list[SubMenuOutSchema], NotFoundSchema],
    status_code=200,
)
async def get_submenus_handler(
    target_menu_id: str,
    response: SubmenuService = Depends(),
) -> list[SubMenuOutSchema] | dict[str, str]:
    """
     Эндпоинт возвращает все подменю
     \f
     :param target_menu_id: str
         Идентификатор меню в БД
    :param response: SubmenuService
         Обьект ответа на запрос из сервиса подменю

     :return: Union[List[SubMenuOutSchema], NotFoundSchema]
         Pydantic-схема для фронтенда с подменю или ошибка
    """
    return await response.read_submenus(target_menu_id=target_menu_id)


@router.post(
    '',
    summary='Публикация подменю',
    response_description='Созданное подменю',
    response_model=Union[SubMenuOutSchema, NotFoundSchema],
    status_code=201,
)
async def post_submenus_handler(
    target_menu_id: str,
    submenu: MenuInSchema,
    response: SubmenuService = Depends(),
) -> SubMenuOutSchema | dict[str, str]:
    """
     Эндпоинт публикации подменю
     \f
     :param target_menu_id: str
         Идентификатор меню в БД
     :param submenu: MenuInSchema
         данные подменю из pedantic-схемы ввода данных
    :param response: SubmenuService
         Обьект ответа на запрос из сервиса подменю

     :return: Union[SubMenuOutSchema, NotFoundSchema]
         Pydantic-схема для фронтенда с подменю или ошибкой
    """
    return await response.create_submenu(target_menu_id=target_menu_id, submenu=submenu)


@router.patch(
    '/{target_submenu_id}',
    summary='Изменение подменю',
    response_description='Измененное подменю',
    response_model=Union[SubMenuOutSchema, NotFoundSchema],
    status_code=200,
)
async def patch_submenu_handler(
    target_menu_id: str,
    target_submenu_id: str,
    submenu: MenuInSchema,
    response: SubmenuService = Depends(),
) -> SubMenuOutSchema | dict[str, str]:
    """
     Эндпоинт изменения меню
     \f
     :param target_menu_id: str
         Идентификатор меню в СУБД
     :param target_submenu_id: str
         Идентификатор подменю в СУБД
     :param submenu: MenuInSchema
         данные подменю из pedantic-схемы ввода данных
    :param response: SubmenuService
         Обьект ответа на запрос из сервиса подменю

     :return: Union[SubMenuOutSchema, NotFoundSchema]
         Pydantic-схема для фронтенда с подменю или ошибкой
    """
    return await response.update_submenu(
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        submenu=submenu,
    )


@router.delete(
    '/{target_submenu_id}',
    summary='Удаление подменю',
    response_description='Сообщение о результате',
    response_model=Union[CorrectDeleteSchema, NotFoundSchema],
    status_code=200,
)
async def delete_submenu_handler(
    target_menu_id: str,
    target_submenu_id: str,
    response: SubmenuService = Depends(),
) -> dict[str, bool | str]:
    """
     Эндпоинт удаления подменю по его id
     \f
     :param target_menu_id: str
         Идентификатор меню в СУБД
     :param target_submenu_id: str
         Идентификатор подменю в СУБД
    :param response: SubmenuService
         Обьект ответа на запрос из сервиса подменю

     :return: Union[CorrectDeleteSchema, NotFoundSchema]
         Pydantic-схема для фронтенда с флагом об удачной операции или ошибкой
    """
    return await response.del_submenu(
        target_menu_id=target_menu_id, target_submenu_id=target_submenu_id
    )
