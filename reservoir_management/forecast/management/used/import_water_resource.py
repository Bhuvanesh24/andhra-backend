import csv,os
from django.core.management.base import BaseCommand
from forecast.models import Andhra_WaterResourceData,andhra_districts

class Command(BaseCommand):
    help = 'Import water resource data from CSV into WaterResourceData model'

    def handle(self, *args, **kwargs):
        csv_file_path = os.path.join(os.path.dirname(__file__), 'resource.csv')

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                district_inst = andhra_districts.objects.get(id=row['District'])
                Andhra_WaterResourceData.objects.create(
                    year=int(row['Year']),
                    month=int(row['Month']),
                    rainfall=float(row['Rainfall']),
                    inflow_states=float(row['Inflow From Other States']),
                    ground_water=float(row['Ground Water']),
                    soil_moisture=float(row['Soil Moisture']),
                    reservoir=float(row['Reservoir']),
                    major=float(row['Major']),
                    medium=float(row['Medium']),
                    mi_tanks=float(row['MI Tanks (Geotagged)']),
                    evapo_trans=float(row['Evapo-99transpiration']),
                    outflow=float(row['Outflow']),
                    river=float(row['River']),
                    micro_basin=float(row['Micro Basin']),
                    consumption=float(row['Consumption']),
                    irrigation=float(row['Irrigation']),
                    industry=float(row['Industry']),
                    domestic=float(row['Domestic']),
                    subsurface_outflow=float(row['Surface and SubSurface Outflow']),
                    district=district_inst
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported water resource data.'))
