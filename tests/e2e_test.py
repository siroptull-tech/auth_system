import requests

BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"

USER_DATA = {
    "email": "sanya_it@example.com",
    "username": "sanya_dev",
    "full_name": "Alexander IT",
    "password": "super_secret_password_123"
}

def test_full_cycle():
    print("Начинаю проверку полного цикла...")
    print("Шаг 1: Проверка Healthcheck...", end=" ")
    try:
        resp = requests.get(HEALTH_URL, timeout=5)
        if resp.status_code == 200:
            print("OK")
        else:
            print(f"Ошибка: статус {resp.status_code}")
            return
    except Exception as e:
        print(f"Сервер недоступен: {e}")
        return

    print("Шаг 2: Регистрация пользователя...", end=" ")
    resp = requests.post(f"{BASE_URL}/auth/register", json=USER_DATA)
    if resp.status_code in [200, 201]:
        print("OK")
    elif resp.status_code == 400 or "already exists" in resp.text.lower():
        print("Пользователь уже существует (ок для теста)")
    else:
        print(f"Ошибка {resp.status_code}: {resp.text}")
        return

    print("Шаг 3: Авторизация (Login)...", end=" ")
    login_payload = {
        "email": USER_DATA["email"],
        "password": USER_DATA["password"]
    }
    
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        if token:
            print(" OK (Токен получен)")
        else:
            print("Ошибка: токен отсутствует в ответе")
            return
    else:
        print(f"Ошибка {resp.status_code}: {resp.text}")
        return

    print("Шаг 4: Проверка защищенного ресурса (/users/me)...", end=" ")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if resp.status_code == 200:
        user_info = resp.json()
        print(f"OK (Привет, {user_info.get('username')})")
    else:
        print(f"Ошибка {resp.status_code}: {resp.text}")
        return

    print("\nПОЛНЫЙ ЦИКЛ ПРОВЕРКИ ПРОЙДЕН УСПЕШНО!")

if __name__ == "__main__":
    test_full_cycle()