from enum import IntEnum


class Lenght(IntEnum):
    """Длины полей в приложении Рецептов."""

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
    
 # max_length=Lenght.MAX_LENGT_NAME.value