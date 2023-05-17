# API авторизация пользователя

_с использованием JWT токена_

---

## Стек

* fastapi
* sqlalchemy
* pydantic
* uvicorn
* asyncpg
* redis
* alembic
* jose

---

<a id='requests'></a>
## Устройство API

### POST /register

Ожидает на вход _UserCreate_ с полями: __name, surname, email, password__.

Создаёт и сохраняет пользователя: __(user_id, name, surname, email, is_active, hashed_password)__.

> Поля _name_ и _surname_ только буквенные символы и '-'. Поле _email_ валидируется классом pydantic _EmailStr_. Поле _password_ валидируется регуляркой по буквам двух регистров, длине и цифрам.

Пароль хэшируется библиотекой __passli__ и заносится в Postgres.

> _user_id генерируется библиотекой uuid, классом UUID._

Возвращает _ShowUser_ с полями: __user_id, name, surname, email, is_active__.

> _Поле _email_ уникальное, если в бд уже есть введённая почта возвращается ошибка._

> _Поле _is_active_ нужно для отметки активных пользователей (вместо удаления из базы может отметить "выключенного" пользователя)._

### POST /login

Ожидает на вход _OAuth2PasswordRequestForm_ с полями: __username(email), password__.

Сверяет почту и пароль и возвращает JWT-токен.

> _Токен создаётся на 60 минут (expire)._

> _Если пароль или почта неверные возвращает ошибку._

> _Если токена нет в Redis по ключу почты он генерируется и сохраняется в Redis. Если токен есть в noSQL базе после проверки пароля возвращается токен (не генерируется новый)._

Возвращается _Token_ с полем: __access_token__.

### POST /logout

Доступно только авторизованным пользователям.

Удаляет токен из Redis.

Возвращает _Token_ с полем: __success__.

### POST /task

Доступно только авторизованным пользователям.

Ожидает на вход _TaskCreate_ с полями: __name, content__.

Создаёт и записывает в базу задачу с полями: __user_id, task_id, name, content__.

> _task_id сохраняется с типом UUID._

> _Пользователь может создать запись только от своего имени._

Возвращает _ShowTask_ с полями:__user_id, task_id, name, content__.

### GET /tasks

Доступно только авторизованным пользователям.

Выводит список задач пользователя.

> _Отображаются только задачи текущего пользователя._

Возвращает _ShowTasks_ с полями: __[[user_id, task_id, name, content], ...]__.

### GET /task/{task_id}

Доступно только авторизованным пользователям.

Ожидает на вход __task_id__.

Выводит задачу пользователя.

> _Пользователь может видеть только свои записи._

> _Если записи нет в базе или она не создана этим пользователем возвращается ошибка._

Возвращает _ShowTask_ c полями:__user_id, task_id, name, content__.

### PUT /task/{task_id}

Доступно только авторизованным пользователям.

Ожидает на вход __TaskEdit__ с полями: __task_id, name, content__.

Изменяет содержимое задачи пользователя.

> _Пользователь может менять только свои записи._

> _Если записи нет в базе или она не создана этим пользователем возвращается ошибка._

Возвращает _ShowTask_ c полями:__user_id, task_id, name, content__.

### DELETE /task/{task_id}

Доступно только авторизованным пользователям.

Ожидает на вход __task_id__.

Удаляет задачу пользователя.

> _Пользователь может удалять только свои записи._

> _Если записи нет в базе или она не создана этим пользователем возвращается ошибка._

Возвращает _Success_ с полем: __success__.

### Все запросы

Стоит общее ограничение на количество запросов (сейчас 100 в минуту). Изменяется значение в модуле _config.py_.

---

## <a id='schemes'>__Структура базы данных__</a>

#### Схема сущности <a id='users_scheme'>users</a>:

user_id | name | surname | is_active | hashed_password
:-------|:-----|:-------:|:---------:|:--------------:
uuid.UUID | str | str | bool | str
 ... | ... | ... | ... | ...

>_Сущности [users](#users_scheme) и [tasks](#tasks_scheme) связаны по атрибуту [user_id](#users_scheme) (один ко многим)._

#### Схема сущности <a id='tasks_scheme'>tasks</a>:

user_id | task_id | name | content
:-------|:--------|:----:|:------:
uuid.UUID | uuid.UUID | str | str
 ... | ... | ... | ... 

---

## Как выполнять запросы

1) Запустить API через [docker](#docker).
2) Перейти по ссылке __http:\/\/host:port\/docs\/__.
3) Выполнить нужные [запросы](#requests).

_или через CURL запросы в консоли._

---

## Особенности

> _Подлючен и настроен __Docker__. Используется __docker-compose.yaml__ файл, и __docker_entrypoint.sh__ для автоматической миграции моделей через Alembic._

> _Все сессии подключения к бд происходят через декоратор __utils.decorators.request()__ -> автоматический откат при ошибке, сокращенье повторения кода._

> _Бизнес-логика содержится в модуле __dals.py__ и не зависит от FastAPI._

> _Асинхронный ход в Postgres._

---

## Инструкции

##### Запуск через Docker

1) Выполнить команду:
    ```
    docker-compose up --build
    ```

##### Настройка Alembic:
1) Создать файлы __Alembic__:
    ```
    alembic init -t async alembic
    ```
2) Внести в __alembic.ini__:
    ```
    # alembic.ini
    sqlalchemy.url = postgresql+asyncpg://user:pass@port:host/db_name
    ```
3) Внести в __alembic.env.py__:
    ```
    # alembic.env.py
    from db.models import Base
    target_metadata = Base.metadata
    ```
4) Создание миграции:
    ```
    alembic revision --autogenerate -m 'migration_name'
    ```

##### Настройка переменных окружения

1) Создать файл __.env__:
    ```
    # .env
    POSTGRES_USER=...
    POSTGRES_PASSWORD=...
    POSTGRES_DB=...
    DATABASE_URL=postgresql+asyncpg://user:pass@port:host/db_name
    REDIS_HOST=...
    REDIS_PORT=...
    SECRET=...
    ALGORITHM=...
    ```

---

#### TODO
- Логирование в файл.
- Тесты.
- Добавление кеширования часто запрашиваемых данных в Redis.