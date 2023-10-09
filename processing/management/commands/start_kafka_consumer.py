from typing import Any, Optional
from django.core.management.base import BaseCommand
from processing.kafka_consumer import main

class Command(BaseCommand):
    help = 'Starts the Kafka consumer'

    def handle(self, *args, **options):
        main()
        