import csv
from django.core.management.base import BaseCommand
from reservoir.models import Reservoir
from forecast.models import State
import os

class Command(BaseCommand):
    help = 'Import data from CSV file into the Reservoir model using batch processing'

    def handle(self, *args, **kwargs):
        csv_file_path = os.path.join(os.path.dirname(__file__), 'reservoir.csv')
        batch_size = 1000  

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))
            return

        try:
            with open(csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                batch = []
                for row in reader:
                    try:
                        state_name = row['State'].strip()
                        try:
                            state_instance = State.objects.get(name=state_name)
                        except State.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f"State not found: {state_name}"))
                            continue

                    
                        frl = float(row['FRL'])
                        live_cap_frl = float(row['Live Cap FRL'])
                        level = float(row['Level'])
                        current_live_storage = float(row['Current Live Storage'])
                        year = int(row['Year'])
                        month = int(row['Month'])

                        
                        batch.append(Reservoir(
                            state=state_instance,
                            district=row['District'].strip(),
                            name=row['Reservoir Name'].strip(),
                            agency_name=row['Agency Name'].strip(),
                            frl=frl,
                            live_cap_frl=live_cap_frl,
                            level=level,
                            current_live_storage=current_live_storage,
                            year=year,
                            month=month
                        ))

                       
                        if len(batch) >= batch_size:
                            Reservoir.objects.bulk_create(batch)
                            batch = [] 
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f"Error processing row: {row}, {e}"))
                        continue

            
                if batch:
                    Reservoir.objects.bulk_create(batch)

            self.stdout.write(self.style.SUCCESS(f"Successfully imported data from {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing data: {e}"))
