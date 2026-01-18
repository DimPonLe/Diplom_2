import pytest
import allure
import requests
from urls import *
from helpers import *


class TestUserRegistration:
    
    @allure.title("Успешная регистрация пользователя")
    def test_successful_registration(self, user_data):
        
        response = requests.post(REGISTER, json=user_data)
        data = response.json()
        
        assert all([
            response.status_code == 200,
            data.get("success") is True,
            "accessToken" in data,
            data["accessToken"].startswith("Bearer "),
            "refreshToken" in data,
            "user" in data,
            data["user"].get("email") == user_data["email"],
            data["user"].get("name") == user_data["name"]
        ]), f"Проверка регистрации не пройдена. Ответ: {data}"

    @allure.title("Регистрация с существующим email")
    def test_registration_with_existing_email(self):
        """Тест регистрации с email, который уже существует"""
        user_data = generate_user_data(8)
        first_response = requests.post(REGISTER, json=user_data)
        first_data = first_response.json()
        assert first_response.status_code == 200, "Первый пользователь не создался"
        second_response = requests.post(REGISTER, json=user_data)
        second_data = second_response.json()
        assert all([
            second_response.status_code == 403,
            second_data.get("success") is False,
            second_data.get("message") == "User already exists"
        ]), f"Ожидалась ошибка дублирования. Ответ: {second_data}"
    
    @allure.title("Регистрация без обязательных полей")
    @pytest.mark.parametrize("missing_field", ["email", "password", "name"])
    def test_registration_without_required_fields(self, missing_field):

        user_data = generate_user_data(8)

        del user_data[missing_field]

        response = requests.post(REGISTER, json=user_data)
        data = response.json()
        
        # Проверяем ответ
        assert all([
            response.status_code == 403,
            data.get("success") is False,
            data.get("message") == "Email, password and name are required fields"
        ]), f"Некорректный ответ при отсутствии {missing_field}: {data}"