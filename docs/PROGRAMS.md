# Программы и инструменты

## Обязательное

| Инструмент | Зачем | Установка |
|---|---|---|
| **VS Code** | основной редактор для Python/Java, Git, тестов | `winget install Microsoft.VisualStudioCode` |
| **Python 3.12** | API/UI-автоматизация | уже установлен |
| **Git** | версии, ветки, PR | уже установлен |
| **GitHub CLI (`gh`)** | создание репозиториев, PR, Actions | уже установлен и авторизован |
| **Postman** | ручные API-запросы | `winget install Postman.Postman` |
| **DBeaver Community** | просмотр SQLite/PostgreSQL | `winget install dbeaver.dbeaver` |
| **Docker Desktop** | тестовая среда, docker-compose | уже установлен |

## Для Python-автоматизации

- `pytest`, `httpx`, `requests`, `playwright`, `pytest-html`, `allure-pytest`.
- VS Code extensions: Python, Pylance, REST Client, SQLite Viewer, GitLens.
- Playwright: `pip install playwright` + `playwright install chromium`.

## Для Java-автоматизации

| Инструмент | Зачем | Установка |
|---|---|---|
| **JDK 21 (Temurin)** | Java | `winget install EclipseAdoptium.Temurin.21.JDK` |
| **Maven** | сборка и тесты | `winget install Apache.Maven` |
| **IntelliJ IDEA Community** | IDE для Java | `winget install JetBrains.IntelliJIDEA.Community` |

> Сейчас установлена Java 1.8. Для JUnit 5 / RestAssured / Selenium нужен JDK 21. Ставить перед Фазой 3, не раньше — чтобы не распыляться.

## Дополнительно (по мере роста)

- **Allure** — красивые отчёты.
- **JMeter** или **Locust** — нагрузочное тестирование.
- **Jira (free)** или **YouTrack** — баг-трекинг.
- **TestRail/Qase** — тест-менеджмент (можно бесплатные триалы).
- **WireMock/Responses** — моки API.
- **Jenkins** — альтернатива GitHub Actions (базово).
- **DevTools** — уже в браузере.

## Что не нужно покупать

- PyCharm Professional, IntelliJ Ultimate, платные курсы — не обязательны на старте.
- Всё основное бесплатное: VS Code, Community IDE, GitHub, Actions, Docker Desktop для личного использования.
