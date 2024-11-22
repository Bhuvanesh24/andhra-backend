import csv,os
from django.core.management.base import BaseCommand
from forecast.models import State,Usage

class Command(BaseCommand):
    help = 'Import Usage data from a CSV file'

    def handle(self, *args, **kwargs):
        # Open the CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'usage.csv')
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Get the state using the state index
                try:
                    state = State.objects.get(id=row['State_Index'])
                except State.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"State with index {row['State_Index']} not found."))
                    continue  # Skip to the next row if the state is not found

                # Create a new Usage record
                Usage.objects.create(
                    year=row['Year'],
                    state=state,
                    domestic_use=row['Domestic'],
                    industrial_use=row['Industrial'],
                    irrigation_use=row['Irrigation']
                )

            self.stdout.write(self.style.SUCCESS('Successfully imported usage data.'))
