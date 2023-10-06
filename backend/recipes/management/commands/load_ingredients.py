import csv
from typing import Any
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда python manage.py 'load_ingredients' загружает ингредиенты
    в базу из csv файла, который располагается в директории /data/... ."""

    def handle(self, *args: Any, **options: Any) -> str:
        try:
            self.import_ingredients_csv()
            print('Загрузка ингредиентов произошла успешно!')
        except Exception:
            raise ('Ошибка при загрузке ингредиентов:')
            
        return 'Обработка файла завершена.'

    def import_ingredients_csv(self, file='data/ingredients.csv'):
        with open(file, newline='', encoding='utf-8') as file_all:
            reader = csv.reader(file_all)
            for row in reader:
                name, measurement_unit, *_ = row
                status, created = Ingredient.objects.update_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
