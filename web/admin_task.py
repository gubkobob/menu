import asyncio
from datetime import timedelta

import openpyxl
from celery import Celery
from google_sheets.google_sheets import GoogleSheet
from project.database import get_async_redis_client
from project.repository_overal_for_admin_task import (
    DishType,
    MenuType,
    SubmenuType,
    update_dish_data_from_file_to_db,
    update_menu_data_from_file_to_db,
    update_submenu_data_from_file_to_db,
)

filename = 'project/admin/Menu.xlsx'
loop = asyncio.get_event_loop()


async def read_excel_to_data(
    filename: str,
) -> dict[str, list[MenuType] | list[SubmenuType] | list[DishType]]:
    """
    Чтение файла Excel и преобразование его в нужный формат данных.
    """
    wb = openpyxl.load_workbook(filename)
    sheet = wb.active

    menus = []
    submenus = []
    dishes = []

    last_menu_id = None
    last_submenu_id = None

    for row in sheet.iter_rows(values_only=True):
        if row[0] is not None:  # Это меню
            last_menu_id = str(row[0])
            menus.append((str(row[0]), str(row[1]), str(row[2])))
        elif row[1] is not None:  # Это подменю
            last_submenu_id = str(row[1])
            submenus.append((last_menu_id, str(row[1]), str(row[2]), str(row[3])))
        elif row[2] is not None:  # Это блюдо
            try:
                discount = row[6]  # Смотрим есть ли столбец скидок
            except IndexError:
                discount = None
            dishes.append(
                (
                    last_menu_id,
                    last_submenu_id,
                    str(row[2]),
                    str(row[3]),
                    str(row[4]),
                    str(row[5]),
                    discount,
                )
            )
        else:
            pass
    return {'menus': menus, 'submenus': submenus, 'dishes': dishes}


async def read_gs_to_data() -> dict[str, list[MenuType] | list[SubmenuType] | list[DishType]]:
    """
    Чтение файла Google sheet и преобразование его в нужный формат данных.
    """
    range = 'Test List!A1:G18'
    gs = GoogleSheet()
    values_from_gs = gs.download(range_name=range)

    menus = []
    submenus = []
    dishes = []

    last_menu_id = None
    last_submenu_id = None

    for row in values_from_gs:
        if row[0]:  # Это меню
            last_menu_id = str(row[0])
            menus.append((str(row[0]), str(row[1]), str(row[2])))
        elif row[1]:  # Это подменю
            last_submenu_id = str(row[1])
            submenus.append((last_menu_id, str(row[1]), str(row[2]), str(row[3])))
        elif row[2]:  # Это блюдо
            try:
                discount = float(row[6])  # Смотрим есть ли столбец скидок
            except IndexError:
                discount = None
            dishes.append(
                (
                    last_menu_id,
                    last_submenu_id,
                    str(row[2]),
                    str(row[3]),
                    str(row[4]),
                    str(row[5]),
                    discount,
                )
            )
        else:
            pass
    return {'menus': menus, 'submenus': submenus, 'dishes': dishes}


celery_app = Celery('admin_task')

celery_app.conf.update(
    broker_url='pyamqp://guest:guest@rabbitmq:5672//',
    result_backend='rpc://',
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Europe/Moscow',
    enable_utc=True,
    beat_schedule={
        'main': {
            'task': 'admin_task.main',
            'schedule': timedelta(seconds=15),
        },
    },
)


async def main_async() -> None:

    # Закомментировать ненужное и оставить нужный сервис - чтение их exel/google sheets
    # current_data = await read_excel_to_data(filename=filename)
    current_data = await read_gs_to_data()

    redis_client = await get_async_redis_client()
    await redis_client.flushdb()
    await update_menu_data_from_file_to_db(menus=current_data['menus'])
    await update_submenu_data_from_file_to_db(submenus=current_data['submenus'])
    await update_dish_data_from_file_to_db(dishes=current_data['dishes'])


@celery_app.task
def main() -> None:
    result = loop.run_until_complete(main_async())
    return result
