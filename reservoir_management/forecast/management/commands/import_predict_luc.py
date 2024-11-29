import csv
import os
from django.core.management.base import BaseCommand
from forecast.models import District,LucPredictionDist # Make sure you import the District model

class Command(BaseCommand):
    help = 'Import reservoir data from reservoir.csv into the Reservoir model'

    def handle(self, *args, **kwargs):
        # Specify the path to your CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'predicted_luc.csv')

        # Open the CSV file
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        # Fetch the district object using the district_id from the CSV
                        district = District.objects.get(id=int(row['District']))

                        # Create and save a Reservoir object for each row in the CSV
                        LucPredictionDist.objects.create(
                            built_up = float(row['Built-Up']),
                            agriculuture = float(row['Agricultural']),
                            forest  = float(row['Forest']),
                            wasteland = float(row['WasteLands']),
                            wetlands = float(row['Wetlands']),
                            waterbodies = float(row['Waterbodies']),
                            year = int(row['Year']),
                            district=district,       
                        )

                        self.stdout.write(
                            self.style.SUCCESS(f"Successfully added LucPrediction: {row['Year']} with District: {district.name}")
                        )
                    except District.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f"District ID {row['District']} not found for LucPrediction: {row['Reservoir']}")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error processing row {row}: {e}")
                        )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
