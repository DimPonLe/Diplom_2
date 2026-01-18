import allure
import pytest
import requests
from urls import *
from helpers import create_order
from data import INVALID_INGREDIENTS, ERROR_MESSAGES


class TestCreateOrder:
    
    @allure.feature("Создание заказа")
    @allure.story("Успешное создание заказа с авторизацией")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_order_with_auth(self, authorized_user_with_token, valid_ingredients):
        with allure.step("Проверка наличия авторизованного пользователя"):
            assert authorized_user_with_token is not None
            assert valid_ingredients is not None
            assert len(valid_ingredients) >= 2
        
        with allure.step("Получение access token"):
            access_token = authorized_user_with_token["access_token"]
        
        with allure.step("Создание заказа с авторизацией"):
            response = create_order(access_token, valid_ingredients[:2])
        
        with allure.step("Проверка статуса ответа"):
            assert response.status_code == 200
        
        with allure.step("Проверка структуры ответа"):
            response_data = response.json()
            assert response_data["success"] is True
            assert "name" in response_data
            assert "order" in response_data
        
        with allure.step("Проверка данных заказа"):
            order_info = response_data["order"]
            assert "number" in order_info
            assert isinstance(order_info["number"], int)
            assert order_info["number"] > 0
            assert response_data["name"]
        
        with allure.step("Запись дополнительной информации в отчет"):
            allure.attach(f"Номер заказа: {order_info['number']}", name="Номер заказа")
            allure.attach(f"Название бургера: {response_data['name']}", name="Название бургера")

    @allure.feature("Создание заказа")
    @allure.story("Успешное создание заказа с валидными ингредиентами")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_order_with_valid_ingredients(self, authorized_user_with_token, valid_ingredients):
        with allure.step("Подготовка тестовых данных"):
            assert authorized_user_with_token is not None
            assert valid_ingredients is not None
            assert len(valid_ingredients) >= 2
        
        with allure.step("Получение токена авторизации"):
            access_token = authorized_user_with_token["access_token"]
        
        with allure.step("Отправка запроса на создание заказа"):
            response = create_order(access_token, valid_ingredients[:2])
        
        with allure.step("Валидация успешного ответа"):
            assert response.status_code == 200
        
        with allure.step("Анализ ответа сервера"):
            response_data = response.json()
            assert response_data["success"] is True
            assert "name" in response_data
            assert "order" in response_data
        
        with allure.step("Проверка деталей заказа"):
            order_info = response_data["order"]
            assert "number" in order_info
            assert isinstance(order_info["number"], int)
            assert order_info["number"] > 0
            assert response_data["name"]
        
        with allure.step("Логирование результатов"):
            allure.attach(str(response_data), name="Полный ответ API")
            allure.attach(f"Использованные ингредиенты: {valid_ingredients[:2]}", name="Ингредиенты")

    @allure.feature("Создание заказа")
    @allure.story("Поток работы с неавторизованным пользователем")
    @allure.severity(allure.severity_level.NORMAL)
    def test_order_creation_flow_for_unauthorized_user(self, user_data, valid_ingredients):
        with allure.step("Проверка наличия ингредиентов"):
            assert valid_ingredients is not None
        
        with allure.step("Создание заказа без авторизации (должно быть доступно)"):
            response_without_auth = create_order(None, valid_ingredients[:2])
        
        with allure.step("Проверка успешного создания заказа без авторизации"):
            assert response_without_auth.status_code == 200
        
        with allure.step("Анализ ответа"):
            response_data = response_without_auth.json()
            assert response_data["success"] is True
            assert "order" in response_data
            allure.attach(f"Номер заказа: {response_data['order']['number']}", name="Заказ без авторизации")
        
        with allure.step("Регистрация нового пользователя"):
            register_response = requests.post(REGISTER, json=user_data)
            assert register_response.status_code == 200
        
        with allure.step("Получение токена после регистрации"):
            register_data = register_response.json()
            access_token = register_data["accessToken"]
        
        with allure.step("Создание заказа после авторизации"):
            order_response = create_order(access_token, valid_ingredients[:2])
            assert order_response.status_code == 200
        
        with allure.step("Проверка успешного создания заказа с авторизацией"):
            order_data = order_response.json()
            assert order_data["success"] is True
            assert "order" in order_data
            assert "number" in order_data["order"]
            allure.attach(f"Номер созданного заказа: {order_data['order']['number']}", name="Номер заказа")
        
        with allure.step("Очистка тестовых данных"):
            from helpers import logout_user, delete_user_by_token
            refresh_token = register_data["refreshToken"]
            if refresh_token:
                logout_user(refresh_token)
            if access_token:
                delete_user_by_token(access_token)

    @allure.feature("Создание заказа")
    @allure.story("Попытка создания заказа без ингредиентов")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_order_without_ingredients_fails(self, authorized_user_with_token):
        with allure.step("Подготовка тестового пользователя"):
            assert authorized_user_with_token is not None
        
        with allure.step("Получение токена авторизации"):
            access_token = authorized_user_with_token["access_token"]
        
        with allure.step("Попытка создания заказа с пустым списком ингредиентов"):
            response = create_order(access_token, [])
        
        with allure.step("Проверка ошибки валидации"):
            assert response.status_code == 400
        
        with allure.step("Анализ сообщения об ошибке"):
            response_data = response.json()
            assert response_data["success"] is False
            expected_message = ERROR_MESSAGES["INGREDIENTS_REQUIRED"]
            assert response_data["message"] == expected_message
            allure.attach(f"Ожидаемое сообщение: {expected_message}", name="Валидация")

    @allure.feature("Создание заказа")
    @allure.story("Попытка создания заказа с невалидным хешем ингредиентов")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_order_with_invalid_ingredient_hash_fails(self, authorized_user_with_token):
        with allure.step("Подготовка тестового пользователя"):
            assert authorized_user_with_token is not None
        
        with allure.step("Получение токена авторизации"):
            access_token = authorized_user_with_token["access_token"]
        
        with allure.step("Создание невалидных хешей ингредиентов"):
            invalid_ingredients = INVALID_INGREDIENTS[:2]
            allure.attach(f"Невалидные ингредиенты: {invalid_ingredients}", name="Тестовые данные")
        
        with allure.step("Попытка создания заказа с невалидными ингредиентами"):
            response = create_order(access_token, invalid_ingredients)
        
        with allure.step("Проверка внутренней ошибки сервера"):
            assert response.status_code == 500
        
        with allure.step("Проверка наличия ответа от сервера"):
            # Просто проверяем, что сервер что-то вернул
            assert response.text, "Сервер должен вернуть ответ"
            allure.attach(response.text, name="Ответ сервера")

    @allure.feature("Создание заказа")
    @allure.story("Попытка создания заказа с пустым массивом ингредиентов")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_order_with_empty_ingredients_array_fails(self, authorized_user_with_token):
        with allure.step("Подготовка тестового пользователя"):
            assert authorized_user_with_token is not None
        
        with allure.step("Получение токена авторизации"):
            access_token = authorized_user_with_token["access_token"]
        
        with allure.step("Попытка создания заказа с пустым массивом"):
            response = create_order(access_token, [])
        
        with allure.step("Проверка ошибки валидации"):
            assert response.status_code == 400
        
        with allure.step("Верификация сообщения об ошибке"):
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == ERROR_MESSAGES["INGREDIENTS_REQUIRED"]
            allure.attach(f"Статус код: {response.status_code}", name="HTTP статус")
            allure.attach(f"Сообщение: {response_data['message']}", name="Детали ошибки")