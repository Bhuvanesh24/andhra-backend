import csv,os
from django.core.management.base import BaseCommand, CommandError
from forecast.models import Usage, District  # Update `myapp` with your app name


class Command(BaseCommand):
    help = "Import usage data from a CSV file into the Usage model."

    def handle(self, *args, **options):
        csv_file_path = os.path.join(os.path.dirname(__file__), 'usage_final.csv')
        
        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                row_count = 0
                for row in reader:
                    try:
                        # Map district using its name or ID
                        district_id = row.get('District')  # Adjust column name
                        district = District.objects.get(id=district_id)

                        # Create a Usage instance
                        usage_instance = Usage.objects.create(
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
                            evapo_trans=float(row['Evapo-transpiration']),
                            outflow=float(row['Outflow']),
                            river=float(row['River']),
                            micro_basin=float(row['Micro Basin']),
                            consumption=float(row['Consumption']),
                            irrigation=float(row['Irrigation']),
                            industry=float(row['Industry']),
                            domestic=float(row['Domestic']),
                            subsurface_outflow=float(row['Surface and SubSurface Outflow']),
                            district=district
                        )
                        row_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"Successfully imported: {usage_instance}"
                        ))

                    except District.DoesNotExist:
                        self.stderr.write(f"Error: District with ID {district_id} not found. Skipping row.")
                    except ValueError as e:
                        self.stderr.write(f"Error processing row: {row}. Error: {str(e)}")
            
            self.stdout.write(self.style.SUCCESS(f"Finished importing {row_count} rows into the Usage model."))

        except FileNotFoundError:
            raise CommandError(f"File '{csv_file_path}' does not exist.")
        except Exception as e:
            raise CommandError(f"An error occurred: {str(e)}")
