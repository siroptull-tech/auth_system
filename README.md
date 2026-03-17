# Authentication & Authorization System

Полнофункциональная система аутентификации и разграничения прав доступа на базе FastAPI, PostgreSQL и JWT.

## Возможности

### Аутентификация
- ✅ Регистрация пользователи с валидацией email
- ✅ Логин с генерацией JWT токенов
- ✅ Логаут (стателесс)
- ✅ Хеширование паролей с bcrypt
- ✅ Мягкое удаление пользователей (is_active флаг)

### Управление пользователями
- ✅ Получение профиля пользователя
- ✅ Обновление профиля (полное имя пароль)
- ✅ Список активных пользователей
- ✅ Удаление аккаунта (деактивация)

### Система разграничения прав
- ✅ Управление ролями (RBAC)
- ✅ Управление разрешениями (Permissions)
- ✅ Связь между пользователями и ролями
- ✅ Связь между ролями и разрешениями
- ✅ Бизнес-объекты для контроля доступа

### Безопасность
- ✅ JWT токены с истечением
- ✅ Bearer authentication
- ✅ Защита маршрутов от неавторизованного доступа
- ✅ CORS поддержка
- ✅ Валидация входных данных через Pydantic


### Документация API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Примеры запросов

#### 1. Регистрация
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

#### 2. Логин
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### 3. Получение профиля (требует токен)
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 4. Обновление профиля
```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "password": "newpassword456"
  }'
```

#### 5. Создание роли (админ)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/roles" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "admin",
    "description": "Administrator role"
  }'
```

## Развертывание в продакшен

### Подготовка
1. Установите переменные окружения в `.env` файл:
   ```
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   JWT_SECRET=your_generated_secret
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

2. Примените миграции базы данных:
   ```bash
   alembic upgrade head
   ```

### Запуск с Docker
```bash
docker-compose -f docker-compose.prod.yml up --build
```

### Проверка
- Health check: `GET /health`
- API docs: `/docs`
- Логи: `app.log`
```

## Модели данных

### User
- `id`: Integer (Primary Key)
- `email`: String (Unique)
- `username`: String (Unique)
- `hashed_password`: String
- `full_name`: String (Optional)
- `is_active`: Boolean (Default: True)
- `created_at`: DateTime
- `updated_at`: DateTime

### Role
- `id`: Integer (Primary Key)
- `name`: String (Unique)
- `description`: String (Optional)
- `is_active`: Boolean (Default: True)
- `created_at`: DateTime
- `updated_at`: DateTime

### Permission
- `id`: Integer (Primary Key)
- `name`: String
- `action`: String (read, write, delete и т.д.)
- `description`: String (Optional)
- `business_element_id`: Foreign Key
- `created_at`: DateTime
- `updated_at`: DateTime

### BusinessElement
- `id`: Integer (Primary Key)
- `name`: String (Unique)
- `description`: String (Optional)
- `resource_type`: String
- `created_at`: DateTime
- `updated_at`: DateTime

## Окружение переменных

Создайте файл `.env` с следующими переменными:

```
DEBUG=True
DATABASE_URL=postgresql://auth_user:auth_password@localhost:5432/auth_db
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
APP_NAME=Auth System
API_V1_PREFIX=/api/v1
```

## Безопасность

### Рекомендации для production

1. **JWT_SECRET**: Используйте сильный ключ (минимум 32 символа)
   ```bash
   openssl rand -hex 32
   ```

2. **CORS**: Ограничьте `allow_origins` до нужных доменов

3. **HTTPS**: Используйте HTTPS в production

4. **Password**: Установите требования к сложности пароля

5. **Rate limiting**: Добавьте ограничение на количество попыток логина

6. **Database**: Используйте безопасные пароли БД и ограничьте доступ

## Структура эндпоинтов

### Auth (`/api/v1/auth`)
- `POST /auth/register` - Регистрация
- `POST /auth/login` - Логин
- `POST /auth/logout` - Логаут

### Users (`/api/v1/users`)
- `GET /users/me` - Получить профиль
- `GET /users` - Список пользователей
- `GET /users/{user_id}` - Получить пользователя
- `PUT /users/{user_id}` - Обновить пользователя
- `DELETE /users/{user_id}` - Удалить пользователя

### Admin (`/api/v1/admin`)
- `POST /admin/roles` - Создать роль
- `GET /admin/roles` - Список ролей
- `GET /admin/roles/{role_id}` - Получить роль
- `POST /admin/users/{user_id}/roles/{role_id}` - Назначить роль
- `POST /admin/permissions` - Создать разрешение
- `GET /admin/permissions` - Список разрешений
- `GET /admin/permissions/{permission_id}` - Получить разрешение
- `POST /admin/roles/{role_id}/permissions/{permission_id}` - Назначить разрешение
- `POST /admin/business-elements` - Создать бизнес-объект
- `GET /admin/business-elements` - Список бизнес-объектов
- `GET /admin/business-elements/{element_id}` - Получить бизнес-объект

### Mock Business (`/api/v1/mock-business`)
- `GET /mock-business/invoices` - Получить счета
- `POST /mock-business/invoices` - Создать счет
- `DELETE /mock-business/invoices/{invoice_id}` - Удалить счет
- `GET /mock-business/reports` - Получить отчеты
- `GET /mock-business/documents` - Получить документы

## Contributing

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## Лицензия

MIT License

## Контакты

- Email: support@authsystem.dev
- Issues: https://github.com/authsystem/issues

---

**Созданно для: Система аутентификации и разграничения прав доступа**
