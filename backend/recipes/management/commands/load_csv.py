import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка csv файлов в базу данных'

    def importingredient(self):
        if Ingredient.objects.exists():
            print('Данные для Ingredient уже загружены.')
        else:
            csv_file_path = os.path.join(
                settings.BASE_DIR, 'data', 'ingredients.csv')
            with open(csv_file_path, 'r', encoding='utf8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Ingredient.objects.create(
                        name=row['name'],
                        measurement_unit=row['measurement_unit']
                    )
                print('Данные для Ingredient успешно загружены!')

    def handle(self, *args, **kwargs):
        self.importingredient()
