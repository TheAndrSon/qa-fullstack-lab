# Пет-проекты

## 1. ShopSphere (готов)

Учебный интернет-магазин: FastAPI + SQLite + Jinja2.

**Функции**
- Регистрация/логин/логаут, роли admin/user.
- Каталог: поиск, категории, пагинация.
- Карточка товара.
- Корзина: добавить/изменить/удалить.
- Checkout и история заказов.
- Админка: создание/удаление товаров.
- JSON API для автоматизации.

**Тестовые пользователи**
- `admin@shopsphere.local` / `Admin123!`
- `alice@example.com` / `User123!`
- `bob@example.com` / `User123!`

**Запуск**
```powershell
uvicorn apps.shopsphere.main:app --reload --port 8000
```

**API**
- `POST /api/register`, `POST /api/login`, `POST /api/logout`
- `GET /api/products`, `GET /api/products/{id}`
- `POST /api/cart`, `GET /api/cart`
- `POST /api/checkout`, `GET /api/orders`
- `GET /api/me`
- `POST /api/admin/products`, `DELETE /api/admin/products/{id}`

**Известные баги** — см. `docs/INSTRUCTOR_BUGS.md`. Не открывать до прохождения.

## 2. TaskFlow (следующий этап)

API-трекер задач для практики API/БД:
- Пользователи, проекты, задачи, роли.
- Фильтры, пагинация, дедлайны.
- JWT или session auth.
- Тесты: pytest + RestAssured, проверка БД.

Создаём в Фазе 2–3, когда база Python уже освоена.

## Упражнения

### Уровень 1 — ручное
- Пройти чек-лист из `MANUAL_TESTING.md`.
- Найти 5 багов, оформить по шаблону.
- Составить тест-план на checkout.

### Уровень 2 — API
- 10 позитивных и 10 негативных API-тестов.
- Проверка БД после checkout.
- Тесты на IDOR (чужой заказ).
- Параметризация и фикстуры.

### Уровень 3 — UI + CI
- Page Object для логина/каталога/корзины.
- 8 UI-тестов Playwright.
- Скриншоты при падении.
- CI на push/PR + артефакт отчёта.

### Уровень 4 — Java
- Порт API-тестов на RestAssured.
- 5 UI-тестов Selenium.
- Maven-профили local/CI.
- Java pipeline.

### Уровень 5 — полный цикл
- Ветка → тесты → PR → review → CI → merge.
- Issue на баг, PR с фиксом, тест на регресс.
- Docker-compose: приложение + тесты.
- Allure-отчёт.
