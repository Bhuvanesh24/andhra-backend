import csv
import os
from django.core.management.base import BaseCommand
from reservoir.models import Reservoir
from forecast.models import District  # Make sure you import the District model

class Command(BaseCommand):
    help = 'Import reservoir data from reservoir.csv into the Reservoir model'

    def handle(self, *args, **kwargs):
        # Specify the path to your CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'reservoir.csv')

        # Open the CSV file
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        # Fetch the district object using the district_id from the CSV
                        district = District.objects.get(id=int(row['district_id']))

                        # Create and save a Reservoir object for each row in the CSV
                        Reservoir.objects.create(
                            id=int(row['reservoir_id']),  # Use the provided ID as the primary key
                            name=row['Reservoir'],   # Assuming 'name' is a field in your Reservoir model
                            district=district,       # Assign the correct district ForeignKey
                        )

                        self.stdout.write(
                            self.style.SUCCESS(f"Successfully added Reservoir: {row['Reservoir']} with District: {district.name}")
                        )
                    except District.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f"District ID {row['district_id']} not found for Reservoir: {row['Reservoir']}")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error processing row {row}: {e}")
                        )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
