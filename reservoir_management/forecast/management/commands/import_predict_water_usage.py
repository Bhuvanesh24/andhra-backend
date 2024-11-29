import csv
import os
from django.core.management.base import BaseCommand
from forecast.models import District,Usage # Make sure you import the District model

class Command(BaseCommand):
    help = 'Import reservoir data from reservoir.csv into the Reservoir model'

    def handle(self, *args, **kwargs):
        # Specify the path to your CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'predicted_water_usage_with_luc.csv')

        # Open the CSV file
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        # Fetch the district object using the district_id from the CSV
                        district = District.objects.get(id=int(row['District']))

                        # Create and save a Reservoir object for each row in the CSV
                        UsagePredictionDist.objects.create(
                            year = row['Year'],
                            month = row['Month'],
                            rainfall  = row['Rainfall'],
                            inflow_states = row['Inflow From Other States'],
                            consumption = row['Consumption'],
                            irrigation = row['Irrigation'],
                            industry = row['Industry'],
                            domestic = row['Domestic'],
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
