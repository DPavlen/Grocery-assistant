# from django.core.validators import RegexValidator

# from core.constants import Lenght


# class SlugValidator(RegexValidator):
#     """Валидация поля Slug-названия тега и его соответсвие."""
#     regex = r'^[-a-zA-Z0-9_]+$'
#     Lenght.MAX_LENGT_NAME_SLUG.value
#     message = (
#         f'Введите правильный слаг тега'
#         f'Slug должен содержать только:\
#         буквы (строчные и заглавные), цифры, дефисы и подчеркивания.'
#         f'Длина не более {Lenght.MAX_LENGT_NAME_SLUG.value} символов'
#     )
#     code = 'invalid_slug'


# class ColorValidator(RegexValidator):
#     """Валидация поля color-Цвет в формате HEX и его соответсвие."""
#     regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
#     Lenght.MAX_LENGT_NAME_COLOR.value
#     message = (
#         f'Введенное значение не является цветом в формате HEX! '
#         f'Длина не более {Lenght.MAX_LENGT_NAME_COLOR.value} символов'
#     )
#     code = 'invalid_slug'
