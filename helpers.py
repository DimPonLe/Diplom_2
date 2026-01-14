# helpers.py
import requests
from urls import *


def delete_user_by_token(access_token):
    """Удаление пользователя по access token"""
    if not access_token:
        return None
    
    headers = {"Authorization": access_token}
    try:
        response = requests.delete(USER, headers=headers)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при удалении пользователя: {e}")
        return None


def login_user(email, password):
    """Вход пользователя"""
    try:
        response = requests.post(
            LOGIN,
            json={"email": email, "password": password}
        )
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при входе пользователя: {e}")
        return None


def logout_user(refresh_token):
    """Выход пользователя из системы"""
    if not refresh_token:
        return None
    
    try:
        response = requests.post(
            LOGOUT,
            json={"token": refresh_token}
        )
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выходе пользователя: {e}")
        return None


def create_order(access_token, ingredients):
    """Создание заказа"""
    headers = {}
    if access_token:
        headers["Authorization"] = access_token
    
    try:
        response = requests.post(
            ORDERS,
            headers=headers,
            json={"ingredients": ingredients}
        )
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании заказа: {e}")
        return None


def get_ingredients():
    """Получение списка ингредиентов"""
    try:
        response = requests.get(INGREDIENTS)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении ингредиентов: {e}")
        return None