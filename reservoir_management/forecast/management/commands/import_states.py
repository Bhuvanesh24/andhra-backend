import csv,os
from django.core.management.base import BaseCommand
from forecast.models import State

class Command(BaseCommand):
    help = 'Import states from a CSV file'

    def handle(self, *args, **kwargs):
        csv_file_path = os.path.join(os.path.dirname(__file__), 'states.csv')
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Assuming 'State' is the name and 'Index' is the ID (primary key)
                state_name = row['State']
                state_id = row['Index']
                State.objects.create(id=state_id, name=state_name)

        self.stdout.write(self.style.SUCCESS('Successfully imported states'))
