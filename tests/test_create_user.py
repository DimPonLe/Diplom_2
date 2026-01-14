import pytest
import allure
import requests
from urls import *
from helpers import login_user


class TestUserSignIn:
    
    @allure.feature("Авторизация пользователя")
    @allure.story("Успешный вход существующего пользователя")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signin_existing_user_success(self, registered_user):
        with allure.step("Подготовка тестового пользователя"):
            assert registered_user is not None
        
        with allure.step("Получение учетных данных"):
            user_email = registered_user["email"]
            user_password = registered_user["password"]
        
        with allure.step("Выполнение запроса на вход"):
            response = login_user(user_email, user_password)
        
        with allure.step("Проверка успешного ответа"):
            assert response.status_code == 200
        
        with allure.step("Анализ структуры ответа"):
            response_data = response.json()
            assert response_data["success"] is True
        
        with allure.step("Проверка наличия токенов"):
            assert "accessToken" in response_data
            assert "refreshToken" in response_data
        
        with allure.step("Валидация access token"):
            access_token = response_data["accessToken"]
            assert access_token.startswith("Bearer ")
        
        with allure.step("Проверка refresh token"):
            refresh_token = response_data["refreshToken"]
            assert refresh_token
        
        with allure.step("Верификация данных пользователя"):
            assert "user" in response_data
            user_info = response_data["user"]
            assert user_info["email"] == user_email
            assert user_info["name"] == registered_user["name"]
        
        with allure.step("Логирование результатов"):
            allure.attach(f"Пользователь: {user_email}", name="Учетные данные")
            allure.attach(f"Access Token начинается с: {access_token[:20]}...", name="Токен авторизации")

    @allure.feature("Авторизация пользователя")
    @allure.story("Попытка входа с неверными учетными данными")
    @allure.severity(allure.severity_level.NORMAL)
    def test_signin_with_invalid_password_fails(self, registered_user):
        with allure.step("Подготовка тестового пользователя"):
            assert registered_user is not None
        
        with allure.step("Использование неверного пароля"):
            user_email = registered_user["email"]
            invalid_password = registered_user["password"] + "_wrong"
        
        with allure.step("Попытка входа с неверными данными"):
            response = login_user(user_email, invalid_password)
        
        with allure.step("Проверка ошибки авторизации"):
            assert response.status_code == 401
        
        with allure.step("Анализ ответа сервера"):
            response_data = response.json()
            assert response_data["success"] is False
        
        with allure.step("Проверка сообщения об ошибке"):
            expected_message = "email or password are incorrect"
            assert response_data["message"] == expected_message
        
        with allure.step("Запись информации об ошибке"):
            allure.attach(f"Email: {user_email}", name="Использованный email")
            allure.attach(f"Сообщение об ошибке: {response_data['message']}", name="Детали ошибки")