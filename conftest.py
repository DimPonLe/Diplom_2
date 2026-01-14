import allure
import pytest
import random
import string
import requests
from urls import *
from helpers import *


def generate_random_string(length=10):
    """Генерация случайной строки"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


@pytest.fixture
def user_data():
    """Фикстура с тестовыми данными пользователя"""
    random_suffix = generate_random_string(8)
    data = {
        "email": f"test_user_{random_suffix}@yandex.ru",
        "password": f"password_{random_suffix}",
        "name": f"Username_{random_suffix}"
    }
    
    with allure.step(f"Сгенерированы тестовые данные пользователя: {data['email']}"):
        yield data


@pytest.fixture
def registered_user(user_data):
    """
    Фикстура создает пользователя и возвращает его данные,
    затем выходит из системы и удаляет пользователя после теста.
    """
    access_token = None
    refresh_token = None
    
    with allure.step(f"Регистрация пользователя {user_data['email']}"):
        response = requests.post(REGISTER, json=user_data)
        
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("accessToken")
            refresh_token = response_data.get("refreshToken")
            
            allure.attach(f"Пользователь зарегистрирован: {user_data['email']}", 
                         name="Регистрация")
            allure.attach(f"Access Token получен", name="Токены")
            
            yield {
                "email": user_data["email"],
                "password": user_data["password"],
                "name": user_data["name"],
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_info": response_data.get("user", {})
            }
        else:
            allure.attach(f"Ошибка регистрации: {response.status_code}", 
                         name="Проблема с регистрацией")
            yield None
    
    with allure.step(f"Очистка тестовых данных для {user_data['email']}"):
        if refresh_token:
            logout_response = logout_user(refresh_token)
            if logout_response and logout_response.status_code == 200:
                allure.attach(f"Пользователь вышел из системы", name="Логаут")
        
        if access_token:
            delete_response = delete_user_by_token(access_token)
            if delete_response and delete_response.status_code in [200, 202]:
                allure.attach(f"Пользователь удален", name="Удаление")


@pytest.fixture
def create_user_for_registration_test():
    """
    Фикстура для создания пользователя в тестах регистрации.
    """
    user_data = {
        "email": f"test_user_{generate_random_string(8)}@yandex.ru",
        "password": f"password_{generate_random_string(8)}",
        "name": f"Username_{generate_random_string(8)}"
    }
    
    access_token = None
    
    with allure.step(f"Создание пользователя для теста регистрации: {user_data['email']}"):
        response = requests.post(REGISTER, json=user_data)
        
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("accessToken")
            
            allure.attach(f"Пользователь создан: {user_data['email']}", 
                         name="Создание пользователя")
            
            yield response, user_data, response_data
        else:
            allure.attach(f"Ошибка создания: {response.status_code}", 
                         name="Ошибка создания")
            yield response, user_data, None
    
    with allure.step(f"Удаление тестового пользователя: {user_data['email']}"):
        if access_token:
            delete_user_by_token(access_token)
            allure.attach(f"Пользователь удален", name="Очистка")


@pytest.fixture
def authorized_user_with_token(registered_user):
    """
    Фикстура возвращает авторизованного пользователя с токеном
    """
    with allure.step(f"Авторизация пользователя {registered_user['email']}"):
        response = requests.post(
            LOGIN,
            json={
                "email": registered_user["email"],
                "password": registered_user["password"]
            }
        )
        
        if response.status_code == 200:
            response_data = response.json()
            allure.attach(f"Пользователь авторизован", name="Авторизация")
            
            return {
                "email": registered_user["email"],
                "access_token": response_data["accessToken"],
                "refresh_token": response_data["refreshToken"]
            }
        
        allure.attach(f"Ошибка авторизации: {response.status_code}", 
                     name="Проблема авторизации")
        return None


@pytest.fixture
def valid_ingredients():
    """
    Фикстура для получения валидных ингредиентов
    """
    with allure.step("Получение списка ингредиентов из API"):
        response = get_ingredients()
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success") is True and "data" in data:
                valid_ingredients = [ingredient["_id"] for ingredient in data["data"][:2]]
                allure.attach(f"Получено {len(valid_ingredients)} ингредиентов", 
                             name="Ингредиенты из API")
                return valid_ingredients
        
        allure.attach("Используются тестовые ингредиенты", name="Тестовые данные")
        return ["6043b41abdacab0626a733c6", "609646e4dc916e00276b2870"]