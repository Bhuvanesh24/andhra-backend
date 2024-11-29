import csv
import os
from django.core.management.base import BaseCommand
from forecast.models import Evaporation, District


class Command(BaseCommand):
    help = 'Import evaporation data from evaporation.csv into the Evaporation model'

    def handle(self, *args, **kwargs):
        # Specify the path to your CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), 'evaporation.csv')

        # Open the CSV file
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        # Fetch the District instance by ID
                        district = District.objects.get(pk=row['District'])

                        # Create the Evaporation instance
                        Evaporation.objects.create(
                            district=district,
                            evapo_transpiration=float(row['Average Evapotranspiration']),
                            year=int(row['Year']),
                            month=int(row['Month']),
                            total_evaporation=float(row['Total Evaporation'])
                        )

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully added Evaporation record for District {district} - {row['Year']}/{row['Month']}"
                            )
                        )
                    except District.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f"District with ID {row['District']} does not exist.")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error processing row {row}: {e}")
                        )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
