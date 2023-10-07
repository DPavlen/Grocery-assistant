from enum import IntEnum


class Lenght(IntEnum):
    """Длины полей в приложении Рецептов и Юзеров."""

    # Атрибуты приложения Рецепты
    # Время приготовления Recipe.cooking_time
    MIN_COOKING_TIME = 1
    MAX_COOKING_TIME = 600
    # Максимальная длина поля name(max_length) Ingredient.name
    # Tag.name, Recipe.name
    MAX_LENGT_NAME = 256
    # Максимальная длина единицы измерения Ingredient.measurement_unit
    MAX_LENGT_MEASUREMENT_UNIT = 50
    # Максимальная длина слага тега Tag.slug
    MAX_LENGT_NAME_SLUG = 150
    # Количество ингедиентов CompositionOfDish.amount
    MIN_AMOUNT_INREDIENT = 1
    MAX_AMOUNT_INREDIENT = 100
    
    # Атрибуты приложения Юзеров
    # Максимальная длина поля email User.email
    MAX_LENGHT_EMAIL = 254
    # Максимальная длина поля username User.username
    MAX_LENGHT_USERNAME = 254
    # Максимальная длина поля first_name User.first_name
    MAX_LENGHT_FIRST_NAME = 254
    # Максимальная длина поля last_name User.last_name
    MAX_LENGHT_LAST_NAME = 254
    # Максимальная длина поля password User.password
    MAX_LENGHT_PASSWORD = 150
    # Максимальная длина поля role User.role
    MAX_LENGHT_ROLE = 150

    # page_size = 6 for API PaginationCust.page_size
    PAGE_SIZE = 6

    # Длина логина пользователя
    LENG_LOGIN_USER = 150
