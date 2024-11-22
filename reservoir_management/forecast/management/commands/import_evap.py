import csv,os
from django.core.management.base import BaseCommand
from forecast.models import State , Evaporation

class Command(BaseCommand):
    help = 'Import land use data from luc.csv file into the LandUse model'

    def handle(self, *args, **kwargs):
        # Specify the path to your CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'evaporation.csv')

        # Open the CSV file
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Get the state object based on the state code from the CSV
                state = State.objects.get(id=row['State'])

                # Create and save a LandUse object for each row in the CSV
                Evaporation.objects.create(
                    state=state,
                    district=row['District'],
                    year=row['Year'],
                    month=row['Month'],
                    level=row['level'],
                    volume=row['volume'],
                )

            self.stdout.write(self.style.SUCCESS('Successfully imported evaporation data.'))
