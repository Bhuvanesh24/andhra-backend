import csv,os
from django.core.management.base import BaseCommand
from forecast.models import LandUse, State

class Command(BaseCommand):
    help = 'Import land use data from luc.csv file into the LandUse model'

    def handle(self, *args, **kwargs):
        # Specify the path to your CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'modified_luc.csv')

        # Open the CSV file
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Get the state object based on the state code from the CSV
                state = State.objects.get(id=row['State'])

                # Create and save a LandUse object for each row in the CSV
                LandUse.objects.create(
                    state=state,
                    year=row['Year'],
                    forest_use=row['Forest'],
                    barren_use=row['Barren'],
                    other_use=row['Others'],
                    fallow_use=row['Fallow'],
                    cropped_use=row['Cropped'],
                )

            self.stdout.write(self.style.SUCCESS('Successfully imported land use data.'))
