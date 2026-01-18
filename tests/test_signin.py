import allure
import pytest
import requests
from urls import *
from helpers import login_user


class TestUserSignIn:
    
    @allure.feature("Авторизация пользователя")
    @allure.story("Успешный вход существующего пользователя")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signin_existing_user_success(self, registered_user):
        with allure.step("Проверка наличия зарегистрированного пользователя"):
            assert registered_user is not None
        
        with allure.step("Получение учетных данных пользователя"):
            user_email = registered_user["email"]
            user_password = registered_user["password"]
            allure.attach(f"Email: {user_email}", name="Учетные данные")
        
        with allure.step("Выполнение запроса на вход"):
            response = login_user(user_email, user_password)
        
        with allure.step("Проверка успешного статуса ответа"):
            assert response.status_code == 200
        
        with allure.step("Анализ структуры ответа"):
            response_data = response.json()
            assert response_data["success"] is True
        
        with allure.step("Проверка наличия токенов в ответе"):
            assert "accessToken" in response_data
            assert "refreshToken" in response_data
        
        with allure.step("Валидация формата access token"):
            access_token = response_data["accessToken"]
            assert access_token.startswith("Bearer ")
            allure.attach(f"Access Token: {access_token[:30]}...", name="Токен авторизации")
        
        with allure.step("Проверка наличия refresh token"):
            refresh_token = response_data["refreshToken"]
            assert refresh_token
        
        with allure.step("Проверка данных пользователя в ответе"):
            assert "user" in response_data
            user_info = response_data["user"]
        
        with allure.step("Верификация email пользователя"):
            assert user_info["email"] == user_email
        
        with allure.step("Верификация имени пользователя"):
            assert user_info["name"] == registered_user["name"]
        
        with allure.step("Запись деталей успешного входа"):
            allure.attach(f"Пользователь: {user_info['name']}", name="Имя пользователя")
            allure.attach(f"Email подтвержден: {user_info['email']}", name="Email")
            allure.attach(str(response_data), name="Полный ответ API")

    @allure.feature("Авторизация пользователя")
    @allure.story("Попытка входа с неверным паролем")
    @allure.severity(allure.severity_level.NORMAL)
    def test_signin_with_invalid_password_fails(self, registered_user):
        with allure.step("Проверка наличия тестового пользователя"):
            assert registered_user is not None
        
        with allure.step("Подготовка неверных учетных данных"):
            user_email = registered_user["email"]
            invalid_password = registered_user["password"] + "_wrong"
            allure.attach(f"Email: {user_email}", name="Правильный email")
            allure.attach(f"Неправильный пароль: {invalid_password}", name="Неверные данные")
        
        with allure.step("Попытка входа с неверным паролем"):
            response = login_user(user_email, invalid_password)
        
        with allure.step("Проверка ошибки авторизации"):
            assert response.status_code == 401
        
        with allure.step("Анализ ответа сервера"):
            response_data = response.json()
            assert response_data["success"] is False
        
        with allure.step("Проверка сообщения об ошибке"):
            expected_message = "email or password are incorrect"
            assert response_data["message"] == expected_message
        
        with allure.step("Запись информации о неудачной попытке"):
            allure.attach(f"Статус код: {response.status_code}", name="HTTP статус")
            allure.attach(f"Ожидаемое сообщение: {expected_message}", name="Ожидаемая ошибка")
            allure.attach(f"Полученное сообщение: {response_data['message']}", name="Ответ сервера")
            allure.attach(str(response_data), name="Полный ответ при ошибке")