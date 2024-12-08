import csv
import os
from django.core.management.base import BaseCommand
from reservoir.models import Reservoir,ReservoirScore # Make sure you import the District model

class Command(BaseCommand):
    help = 'Import reservoir data from reservoir.csv into the Reservoir model'

    def handle(self, *args, **kwargs):
        # Specify the path to your CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'score.csv')

        # Open the CSV file
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        # Fetch the district object using the district_id from the CSV
                        res = Reservoir.objects.get(id=int(row['reservoir_id']))

                        # Create and save a Reservoir object for each row in the CSV
                        ReservoirScore.objects.create(
                            mean_storage = float(row['mean storage']),
                            flood_cushion   = float(row['flood cushion']),
                            rainfall  = float(row['rainfall']),
                            evaporation = float(row['evaporation']),
                            population = int(row['Population']),
                            siltation = float(row['Siltation(tmc)']),
                            capacity =  float(row['capacity']),
                            age = int(row['Age']),
                            year = int(row['year']),
                            score  = float(row['score']),
                            reservoir = res     
                        )

                        self.stdout.write(
                            self.style.SUCCESS(f"Successfully added score: {row['year']} with Reservoir: {res.name}")
                        )
                    except res.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f"reservoir ID {row['reservoir_id']} not found for reservoir")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error processing row {row}: {e}")
                        )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
