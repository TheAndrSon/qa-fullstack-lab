# Роадмап: автоматизация для QA с нуля

## Цель и сроки

- **Цель:** уверенный junior/middle QA Automation с Python и Java, Git/GitHub, CI/CD, полным циклом тестирования.
- **Старт:** ручной QA с 3+ годами опыта, без опыта в автоматизации и без Python/Java.
- **Режим:** 10–15 часов в неделю (5 будних дней по 1,5–2 часа + выходные).
- **Реалистичный срок:** **6–9 месяцев** до уверенного middle-уровня.
- **Если заниматься full-time (30–40 ч/нед):** 3–4 месяца.
- **Порядок:** сначала Python (быстрый результат и API/UI-автоматизация), затем Java (enterprise-вакансии).

## Формат недели

- 2 занятия по теории (1–1,5 ч).
- 2–3 практических сессии в репозитории (2–4 ч).
- 1 код-ревью/разбор ошибок (1 ч).
- 1 мини-ретро: что понял, что осталось, что дальше (30 мин).

## Фаза 0. База (недели 1–2)

**Темы**
- Git: commit, branch, merge, rebase, conflict, PR.
- GitHub: issues, PR, review, Actions, secrets.
- Ручное тестирование: тест-дизайн, чек-листы, тест-кейсы, баг-репорты, severity/priority.
- DevTools: Network, Console, Elements, Application.
- Postman: коллекции, окружения, переменные, тесты.
- SQL: SELECT, WHERE, JOIN, GROUP BY, INSERT/UPDATE/DELETE.
- HTTP: методы, статусы, headers, cookies, REST.

**Практика**
- Пройти `docs/MANUAL_TESTING.md`.
- Найти 5 багов в ShopSphere вручную.
- Оформить 5 баг-репортов.
- Создать feature-ветку, PR, пройти CI.

**Результат:** уверенно работаешь с Git/GitHub, умеешь писать тест-план и баг-репорты.

## Фаза 1. Python + API-автоматизация (недели 3–8)

**Python**
- Синтаксис, типы, условия, циклы, функции.
- Коллекции: list, dict, set, tuple.
- Файлы, JSON, исключения.
- ООП: классы, методы, наследование, композиция.
- Модули, пакеты, venv, pip.
- Виртуальное окружение и зависимости.
- Основы typing, comprehensions.

**Тестирование**
- pytest: фикстуры, параметризация, маркеры, assert.
- `requests` / `httpx`: GET/POST, cookies, headers, JSON, auth.
- FastAPI TestClient.
- Валидация схем, негативные тесты, граничные значения.
- Работа с БД: sqlite3, проверка данных после API-запроса.
- Структура тестов: arrange/act/assert, фикстуры, изоляция.

**Практика**
- 20+ API-тестов для ShopSphere.
- Негативные сценарии: неверный пароль, чужой заказ, отрицательное количество.
- Проверка БД после checkout.
- Первый PR с тестами.

**Результат:** пишешь API-тесты на Python и понимаешь, как устроен тестовый фреймворк.

## Фаза 2. UI-автоматизация + CI (недели 9–12)

**Темы**
- Playwright (Python): локаторы, ожидания, клики, формы, скриншоты.
- Page Object Model.
- Стабильность тестов: явные ожидания, изоляция данных.
- Allure / pytest-html: отчёты.
- GitHub Actions: матрицы, кэш, артефакты.
- Запуск в headless, параллельность.

**Практика**
- 8–10 UI-тестов: логин, каталог, корзина, checkout.
- Page Object для ShopSphere.
- CI: тесты на push/PR, артефакт с отчётом.
- Намеренно сломать тест и починить.

**Результат:** стабильные UI-тесты и зелёный pipeline.

## Фаза 3. Java + enterprise-автоматизация (недели 13–20)

**Java**
- Синтаксис, типы, условия, циклы, методы.
- ООП, интерфейсы, коллекции, generics, исключения.
- Maven: структура, зависимости, surefire.
- JUnit 5: аннотации, assertions, параметризация.
- RestAssured: API-тесты.
- Selenium WebDriver: локаторы, ожидания, Page Object.
- Логирование (SLF4J), конфиги.

**Практика**
- Порт 10 API-тестов на Java + RestAssured.
- 5 UI-тестов на Selenium.
- Maven-профили: local/CI.
- Java pipeline в GitHub Actions.

**Результат:** умеешь поддерживать Java-проект и писать тесты на двух языках.

## Фаза 4. Фреймворк и полный цикл (недели 21–24)

**Темы**
- Архитектура тестового фреймворка: слои, конфиги, фабрики, билдеры.
- Тестовые данные и фикстуры.
- Docker: контейнеры, docker-compose, тестовая среда.
- API mocking (WireMock/Responses).
- Работа с БД в тестах.
- Основы performance: Locust/JMeter.
- Основы security: OWASP Top 10, auth, IDOR, XSS.
- CI/CD: GitHub Actions, Jenkins (базово), quality gates.
- Метрики QA: coverage, flaky rate, time to feedback.
- Подготовка к интервью: рассказ о проекте, код-ревью, live-coding.

**Практика**
- Собрать `qa-framework` с Python и Java.
- Добавить Allure-отчёты и параллельный запуск.
- Docker-compose для приложения + тестов.
- Написать тест-стратегию для пет-проекта.
- Финальное портфолио: 2 репозитория, CI-бейджи, отчёты, баг-репорты.

**Результат:** готов к junior/middle automation QA, есть портфолио и история коммитов.

## Контрольные точки

| Когда | Что должно быть |
|---|---|
| Неделя 2 | 5 баг-репортов, первый PR, CI зелёный |
| Неделя 6 | 20 API-тестов на Python |
| Неделя 10 | 8 UI-тестов Playwright + POM |
| Неделя 14 | 10 API-тестов на Java |
| Неделя 18 | 5 UI-тестов Selenium |
| Неделя 22 | Фреймворк + Docker + Allure |
| Неделя 24 | Портфолио и резюме |

## Ресурсы

- Python: «Automate the Boring Stuff», Real Python, официальная документация.
- pytest: docs.pytest.org.
- Playwright: playwright.dev/python.
- FastAPI: fastapi.tiangolo.com.
- Java: «Head First Java», Hyperskill, официальный туториал Oracle.
- JUnit 5, RestAssured, Selenium: официальные docs.
- Git: learngitbranching.js.org, GitHub Skills.
- SQL: sqlbolt.com.
- Тест-дизайн: «How We Test Software at Microsoft», статьи про boundary values/equivalence classes.
- CI: docs.github.com/actions.
- Docker: docs.docker.com/get-started.

## Что делать, если время ограничено

- 5 ч/нед → 10–12 месяцев.
- 20 ч/нед → 4–5 месяцев.
- Главное — не проходить темы «по видео», а закрывать их практикой в репозитории.
