from re import search

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from core.constants import LenghtField


class SlugValidator(RegexValidator):
    """Валидация поля Slug-названия модели тега и его соответсвие."""

    regex = r"^[-a-zA-Z0-9_]+$"
    LenghtField.MAX_LENGT_NAME_SLUG.value
    message = (
        f"Введите правильный слаг тега"
        f"Slug должен содержать только:\
        буквы (строчные и заглавные), цифры, дефисы и подчеркивания."
        f"Длина не более {LenghtField.MAX_LENGT_NAME_SLUG.value} символов"
    )
    code = "invalid_slug"


class ColorValidator(RegexValidator):
    """Валидация поля color-Цвет Тега в формате HEX и его соответсвие."""

    regex = ("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",)
    LenghtField.MAX_LENGT_NAME_COLOR.value
    message = (
        f"Введенное значение не является цветом в формате HEX! "
        f"Длина не более {LenghtField.MAX_LENGT_NAME_COLOR.value} символов"
    )
    code = "invalid_color"


def username_validator(username):
    """Валидация для поля 'Логин пользователя' модели User."""
    if username == "me":
        raise ValidationError("Нельзя использовать имя пользователя me")

    if not search(r"^[a-zA-Z][a-zA-Z0-9-_\.]{1,150}$", username):
        raise ValidationError("В логине Пользователя используются недопустимые символы")


def first_name_validator(first_name):
    """Валидация для поля 'Имя пользователя' модели User."""
    if not search(r"^[A-Za-zА-Яа-я0-9]{1,150}$", first_name):
        raise ValidationError("В имени пользователя используются недопустимые символы")


def last_name_validator(last_name):
    """Валидация для поля 'Фамилия пользователя' модели User."""
    if not search(r"^[A-Za-zА-Яа-я0-9]{1,150}$", last_name):
        raise ValidationError(
            "В фамилии пользователя используются недопустимые символы"
        )
