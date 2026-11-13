# Git, GitHub и CI

## Ветки

```
main        — стабильная версия, только через PR
develop     — интеграционная ветка
feature/*   — учебные задачи
fix/*       — исправления
```

Правила:
- В `main` и `develop` — только через PR.
- Одна задача = одна ветка.
- Перед PR: `git pull --rebase origin develop`, локальные тесты, `pytest -q`.
- PR: описание, что сделано, как проверить, скриншот/лог.
- CI должен быть зелёным до merge.

## Конвенция коммитов

```
feat: add product search API tests
fix: correct cart total calculation
test: add checkout UI test
docs: update roadmap
ci: add Java workflow
```

## Базовый цикл

```powershell
git checkout develop
git pull
git checkout -b feature/api-tests
# ... изменения ...
pytest -q
git add .
git commit -m "test: add auth API tests"
git push -u origin feature/api-tests
gh pr create --base develop --head feature/api-tests --fill
```

## GitHub Actions

- `.github/workflows/python-tests.yml` — pytest на push/PR.
- `.github/workflows/java-tests.yml` — поднимает приложение и запускает Maven-тесты.

Посмотреть статус:
```powershell
gh run list
gh run watch
```

## Упражнения

1. Создать `feature/readme-badge`, добавить бейдж CI в README, открыть PR в `develop`.
2. Сломать один тест в ветке, посмотреть красный CI, починить.
3. Создать issue на найденный баг, привязать PR (`Closes #1`).
4. Сделать `fix/cart-negative-qty`, добавить тест, пройти review.
5. Настроить branch protection для `main` (Require PR + Require status checks).
