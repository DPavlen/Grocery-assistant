import csv
from typing import Any
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

class Command(BaseCommand):
    """Команда python manage.py 'load_ingredients' загружает ингредиенты
    в базу из csv файла, который располагается в директории /data/... ."""
    def handle(self, *args: Any, **options: Any) -> str:
        self.import_ingredients_csv()
        print('Загрузка ингредиентов произошла успешно!')

    def import_ingredients_csv(self, file='data/ingredients.csv'):
        file_path = f'./data{file}'
        with open(file, newline='', encoding='utf-8') as file_all:
            reader = csv.reader(file_all)
            for row in reader:
                status, created = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                ) 