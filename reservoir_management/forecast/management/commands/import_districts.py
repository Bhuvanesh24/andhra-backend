import csv
import os
from django.core.management.base import BaseCommand
from forecast.models import District


class Command(BaseCommand):
    help = 'Import district data from districts.csv into the District model'

    def handle(self, *args, **kwargs):
        # Specify the path to your CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'district.csv')

        # Open the CSV file
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                      
                        District.objects.create(
                            id=int(row['id']),  
                            name=row['name']   
                        )

                        self.stdout.write(
                            self.style.SUCCESS(f"Successfully added District: {row['name']}")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error processing row {row}: {e}")
                        )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
