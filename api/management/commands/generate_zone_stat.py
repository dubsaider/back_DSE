from django.core.management.base import BaseCommand
from datetime import datetime
from api.models import Incident, ZoneStat, CameraStat, Camera, Location
from django.db.models.functions import TruncDate


class Command(BaseCommand):
    help = 'Generates ZoneStat from CameraStat data'

    def handle(self, *args, **options):
        unique_combinations = CameraStat.objects.annotate(
            date=TruncDate('timestamp')
        ).values('date', 'camera__input_location', 'camera__output_location').distinct()

        for combination in unique_combinations:
            input_location = Location.objects.get(id=combination['camera__input_location'])
            output_location = Location.objects.get(id=combination['camera__output_location'])

            count = CameraStat.objects.filter(
                timestamp__date=combination['date'],
                camera__input_location=input_location,
                camera__output_location=output_location,
            ).count()

            zone_stat, created = ZoneStat.objects.get_or_create(
                location=input_location,
                timestamp=combination['date'],
                defaults={'value': count, 'change': count}
            )

            if not created:
                zone_stat.value += count
                zone_stat.change = count - (zone_stat.value - count)
                zone_stat.save()

        self.stdout.write(self.style.SUCCESS('Successfully generated ZoneStat'))