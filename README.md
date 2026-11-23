# Project Manager API

FastAPI-приложение с асинхронным CRUD для сущности `Project`, JWT-авторизацией, кешированием через Redis и PostgreSQL.

## Структура проекта

```
hw_final/
├── app/
│   ├── __init__.py
│   ├── main.py          # Точка входа FastAPI
│   ├── config.py         # Настройки из переменных окружения
│   ├── database.py       # Engine, сессии, Base
│   ├── models.py         # Модели User, Project
│   ├── schemas.py        # Pydantic-схемы
│   ├── auth.py           # JWT, хеширование паролей
│   ├── redis_client.py   # Подключение к Redis
│   └── routers/
│       ├── auth.py       # Регистрация, логин
│       └── projects.py   # CRUD для проектов
├── tests/
│   ├── conftest.py       # Фикстуры pytest
│   └── test_project.py   # Тесты
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── render.yaml
└── .env.example
```

## Запуск локально

1. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

2. Создайте файл `.env` (см. `.env.example`).

3. Убедитесь, что PostgreSQL и Redis запущены локально.

4. Запустите приложение:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Откройте Swagger UI: http://localhost:8000/docs

## Запуск через Docker

1. Создайте файл `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Запустите все сервисы одной командой:
   ```bash
   docker compose up --build
   ```

3. API будет доступно на http://localhost:8000
4. Swagger UI: http://localhost:8000/docs

## Запуск тестов

Тесты запускаются внутри контейнера `web` (где доступны `db` и `redis`):

```bash
docker compose exec web pytest -v
```

Или локально (если запущены PostgreSQL и Redis):
```bash
pytest -v
```

## Эндпоинты

### Авторизация

| Метод | Путь | Описание | Тело |
|-------|------|----------|------|
| POST | `/auth/register` | Регистрация пользователя | `{"username": "...", "email": "...", "password": "..."}` |
| POST | `/auth/login` | Вход, получение JWT | form-data: `username`, `password` |

### Проекты (требуют Bearer-токен)

| Метод | Путь | Описание | Тело |
|-------|------|----------|------|
| GET | `/projects` | Список проектов (с кешированием) | — |
| POST | `/projects` | Создать проект | `{"name": "...", "description": "..."}` |
| GET | `/projects/{id}` | Получить проект | — |
| PUT | `/projects/{id}` | Обновить проект | `{"name": "...", "description": "..."}` |
| DELETE | `/projects/{id}` | Удалить проект | — |

### Health

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка работоспособности |

## Ошибки

| Код | Описание |
|-----|----------|
| 401 | Не авторизован / неверный токен |
| 403 | Нет прав (не владелец проекта) |
| 404 | Проект не найден |

## Пример .env

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=hw_final_db
SECRET_KEY=change-this-in-production
```

## Деплой на Render

1. Загрузите проект в Git-репозиторий (GitHub/GitLab).
2. На [render.com](https://render.com) создайте новый сервис:
   - Type: **Web Service**
   - Environment: **Docker**
   - Repository: ваш репозиторий
3. В разделе **Environment** добавьте переменные:
   - `DATABASE_URL` — Render предоставит URL после создания PostgreSQL
   - `REDIS_URL` — Render предоставит URL после создания Redis
   - `SECRET_KEY` — сгенерируйте случайную строку
4. Создайте базу данных: **New → PostgreSQL** (Free plan).
5. Создайте Redis: **New → Redis** (Free plan).
6. Укажите команду запуска (Render подставит `PORT` автоматически):
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
7. После деплоя проверьте публичный URL:
   - `https://<your-service>.onrender.com/health`
   - `https://<your-service>.onrender.com/docs`

## Технологии

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0 (async)** — ORM
- **asyncpg** — асинхронный драйвер PostgreSQL
- **Redis** — кеширование
- **PyJWT** — JWT-токены
- **bcrypt** — хеширование паролей
- **Docker / Docker Compose** — контейнеризация
