# 🔐 FastAPI Auth System (JWT + RBAC)

Полнофункциональный шаблон системы аутентификации и авторизации для быстрой разработки масштабируемых приложений. Забудь про написание логина и ролей с нуля — всё уже упаковано, протестировано и готово к деплою.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pytest](https://img.shields.io/badge/Coverage-90%25-brightgreen?style=for-the-badge&logo=pytest)](https://docs.pytest.org/)

---

## 🚀 Основные возможности

* 🛡 **Безопасность:** JWT токены (Access/Refresh), хеширование паролей через `bcrypt` и защита от CSRF/XSS.
* 🎭 **Гибкий RBAC:** Ролевая модель доступа (Role-Based Access Control) с поддержкой Permissions. Настройка доступа к любому эндпоинту.
* 🐳 **Docker "под ключ":** Полная оркестрация. Контейнеры сами ждут готовности БД (healthchecks) и накатывают миграции Alembic.
* 🧪 **Надежность:** Покрытие тестами (Pytest) >90%. В комплекте E2E-скрипт для проверки всей цепочки от регистрации до профиля.
* 🏗 **Modern Stack:** SQLAlchemy 2.0 (Async), Pydantic v2 и автоматическая документация.

---

## 🛠 Технологический стек

* **Backend:** FastAPI
* **ORM:** SQLAlchemy 2.0 (Async) + Alembic
* **Database:** PostgreSQL 15
* **DevOps:** Docker & Docker Compose
* **QA:** Pytest + E2E Testing suite

---

### 🛡 Логика авторизации (RBAC)
Доступ проверяется на основе матрицы прав `Access Roles Rules`:
- `read_permission`: Доступ к своим ресурсам.
- `read_all_permission`: Просмотр всех объектов (Менеджер/Админ).
- `create_permission`: Создание новых сущностей.
- `update_all_permission`: Редактирование любых данных (Админ).
