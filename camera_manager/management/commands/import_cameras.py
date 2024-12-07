import csv
from django.core.management.base import BaseCommand
from camera_manager.models import Camera

class Command(BaseCommand):
    help = 'Import cameras from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                camera = Camera(
                    camera_name=row['camera_name'],
                    camera_ip=row['camera_ip'],
                    camera_lat=row['camera_lat'],
                    camera_lon=row['camera_lon'],
                    camera_description=row['camera_description'],
                    is_active=row['is_active'].lower() in ['true', '1']
                )
                camera.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {camera.camera_name}'))