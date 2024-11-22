import csv,os
from django.core.management.base import BaseCommand
from forecast.models import Population

class Command(BaseCommand):
    help = 'Import population data from a CSV file'

    def handle(self, *args, **kwargs):
        # Specify the path to your CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'population.csv')

        # Open the CSV file
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Create a Population object and populate fields from CSV data
                Population.objects.create(
                    year=row['Year'],
                    total_population=row['Population'],
                    urban_population=row['Urban Population'],
                    rural_population=row['Rural Population'],
                )

            self.stdout.write(self.style.SUCCESS('Successfully imported population data.'))
