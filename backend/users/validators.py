from django.contrib.auth.validators import UnicodeUsernameValidator

from core.constants import Lenght


class UsernameValidatorRegex(UnicodeUsernameValidator):
    """Валидация имени пользователя и его соответсвие.
    А также ограничение длины пользователя."""

    regex = r"^[\w.@+-]+\Z"
    flag = 0
    max_length = Lenght.LENG_LOGIN_USER
    message = (
        f"Введите правильное имя пользователя."
        f" Должно содержать буквы, цифры и знаки @/./+/-/_."
        f" Длина не более {Lenght.LENG_LOGIN_USER} символов"
    )
    error_message = {
        "invalid": f"Набор символов не более {Lenght.LENG_LOGIN_USER}. "
        "Только буквы, цифры и @/./+/-/_",
        "required": "Поле не может быть пустым и обязательно!",
    }
