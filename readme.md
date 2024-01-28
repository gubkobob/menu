# Меню ресторана

## 1. Описание проекта:
 REST API по работе с меню ресторана 
## 2. Используемые технологии:
#### - Python 3.10
#### - FastAPI
#### - SQLAlchemy
#### - Pydantic
#### - PostgreSQL
#### - Docker
#### - Alembic
## 3. Техническое задание:
Написать проект на FastAPI с использованием PostgreSQL в качестве БД. В проекте следует реализовать REST API по работе с меню ресторана, все CRUD операции. Даны 3 сущности: Меню, Подменю, Блюдо.

### Зависимости:
- У меню есть подменю, которые к ней привязаны.
- У подменю есть блюда.

### Условия:
- Блюдо не может быть привязано напрямую к меню, минуя подменю.
- Блюдо не может находиться в 2-х подменю одновременно.
- Подменю не может находиться в 2-х меню одновременно.
- Если удалить меню, должны удалиться все подменю и блюда этого меню.
- Если удалить подменю, должны удалиться все блюда этого подменю.
- Цены блюд выводить с округлением до 2 знаков после запятой.
- Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню.
- Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю.


## 4. Установка и запуск
   
### Клонируйте репозитторий и перейдите в корень проекта:
- git clone https://github.com/gubkobob/menu.git
- cd menu
### Создайте .env файл с переменными:
- DB_HOST=db
- DB_PORT=5432
- POSTGRES_DB=postgres
- POSTGRES_USER=admin
- POSTGRES_PASSWORD=admin

- DB_HOST_TEST=db_test
- DB_PORT_TEST=6000
- POSTGRES_DB_TEST=postgres_test
- POSTGRES_USER_TEST=admin
- POSTGRES_PASSWORD_TEST=admin

### Выполните команду для запуска проекта:
#### Только для Unix систем!!!
- docker compose up --build
### Выполните команду для запуска тестов в отдельном когнтейнере:
#### Только для Unix систем!!!
- docker compose -f docker-compose-test.yaml up --build
### Для ручного тестирования эндпоинтов проекта удобно пользоваться следующим URL:
- http://127.0.0.1:8000/docs
### Запрос на получение всех меню с количеством подменю и блюд находится:
- menu/web/project/menus/services.py -> get_menu


