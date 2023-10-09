from re import search
import re

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from core.constants import Lenght


class SlugValidator(RegexValidator):
    """Валидация поля Slug-названия модели тега и его соответсвие."""
    regex = r'^[-a-zA-Z0-9_]+$'
    Lenght.MAX_LENGT_NAME_SLUG.value
    message = (
        f'Введите правильный слаг тега'
        f'Slug должен содержать только:\
        буквы (строчные и заглавные), цифры, дефисы и подчеркивания.'
        f'Длина не более {Lenght.MAX_LENGT_NAME_SLUG.value} символов'
    )
    code = 'invalid_slug'


class ColorValidator(RegexValidator):
    """Валидация поля color-Цвет Тега в формате HEX и его соответсвие."""
    regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
    Lenght.MAX_LENGT_NAME_COLOR.value
    message = (
        f'Введенное значение не является цветом в формате HEX! '
        f'Длина не более {Lenght.MAX_LENGT_NAME_COLOR.value} символов'
    )
    code = 'invalid_color'


class UsernameValidator(RegexValidator):
    def validate(self, username):
        """Валидация для поля 'Логин пользователя' модели User."""  
        if not search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', username):
            raise ValidationError(
                f'В логине пользователя: {username} используются '
                f'недопустимые символы'
            )


class FirstNameValidator(RegexValidator):
    def validate(self, first_name):
        """Валидация для поля 'Имя пользователя' модели User."""  
        if not re.search(r'^[A-Za-zА-Яа-я0-9]{1,150}$', first_name):
            raise ValidationError(
                f'В имени: {first_name} используются '
                f'недопустимые символы'
            )


class LastNameValidator(RegexValidator):
    def validate(self, last_name):
        """Валидация для поля 'Фамилия пользователя' модели User."""  
        if not re.search(r'^[A-Za-zА-Яа-я0-9]{1,150}$', last_name):
            raise ValidationError(
                f'В фамилии: {last_name} используются '
                f'недопустимые символы'
            )
