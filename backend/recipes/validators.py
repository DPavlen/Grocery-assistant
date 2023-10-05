from django.core.validators import RegexValidator


class SlugValidator(RegexValidator):
    """Валидация поля Slug-названия тега и его соответсвие."""
    regex = r'^[-a-zA-Z0-9_]+$'
    max_length = 150
    message = (
        f'Введите правильный слаг тега',
        f'Slug должен содержать только:\
        буквы (строчные и заглавные), цифры, дефисы и подчеркивания.'
        f'Длина не более {max_length} символов'
    )
    code = 'invalid_slug'
