import allure
import pytest
import requests
from urls import *
from helpers import *

@pytest.fixture
def user_data():
    data = generate_user_data(8)  # Используем функцию из helpers
    
    with allure.step(f"Сгенерированы тестовые данные пользователя: {data['email']}"):
        yield data


@pytest.fixture
def registered_user(user_data):
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
                         name="Проблема с регистрации")
            yield None
    
    with allure.step(f"Очистка тестовых данных для {user_data['email']}"):
        if refresh_token:
            logout_user(refresh_token)
        
        if access_token:
            delete_user_by_token(access_token)


@pytest.fixture
def create_user_for_registration_test():
    user_data = generate_user_data(8)  # ← Используем ту же функцию!
    
    access_token = None
    
    with allure.step(f"Создание пользователя для теста регистрации: {user_data['email']}"):
        response = requests.post(REGISTER, json=user_data)
        
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("accessToken")
            
            yield response, user_data, response_data
        else:
            yield response, user_data, None
    
    with allure.step(f"Удаление тестового пользователя: {user_data['email']}"):
        if access_token:
            delete_user_by_token(access_token)


@pytest.fixture
def authorized_user_with_token(registered_user):
    if not registered_user:
        return None
    
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
            
            return {
                "email": registered_user["email"],
                "access_token": response_data["accessToken"],
                "refresh_token": response_data["refreshToken"]
            }
        
        return None


@pytest.fixture
def valid_ingredients():
    with allure.step("Получение списка ингредиентов из API"):
        response = get_ingredients()
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success") is True and "data" in data:
                valid_ingredients = [ingredient["_id"] for ingredient in data["data"][:2]]
                return valid_ingredients
        
        return ["6043b41abdacab0626a733c6", "609646e4dc916e00276b2870"]