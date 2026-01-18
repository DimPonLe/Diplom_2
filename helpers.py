import requests
import random
import string
import logging
from urls import *

logger = logging.getLogger(__name__)

def delete_user_by_token(access_token):
    if not access_token:
        logger.warning("Попытка удаления пользователя без токена")
        return None
    
    headers = {"Authorization": access_token}
    try:
        response = requests.delete(USER, headers=headers)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при удалении пользователя: {e}")
        return None


def login_user(email, password):
    try:
        response = requests.post(
            LOGIN,
            json={"email": email, "password": password}
        )
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при входе пользователя: {e}")
        return None


def logout_user(refresh_token):
    if not refresh_token:
        return None
    
    try:
        response = requests.post(
            LOGOUT,
            json={"token": refresh_token}
        )
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выходе пользователя: {e}")
        return None


def create_order(access_token, ingredients):
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
        logger.error(f"Ошибка при создании заказа: {e}")
        return None


def get_ingredients():
    try:
        response = requests.get(INGREDIENTS)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении ингредиентов: {e}")
        return None
    
def generate_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_user_data(suffix_length=8):
    random_suffix = generate_random_string(suffix_length)
    return {
        "email": f"test_user_{random_suffix}@yandex.ru",
        "password": f"password_{random_suffix}",
        "name": f"Username_{random_suffix}"
    }