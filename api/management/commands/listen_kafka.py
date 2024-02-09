from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
import json
import datetime
from api.models import Incident, ZoneStats


class Command(BaseCommand):
    help = "Listens to Kafka topic and saves incoming messages to the database."

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            "cluster-logs",
            bootstrap_servers=['10.61.36.15:9092', '10.61.36.15:9093', '10.61.36.15:9094'],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )

        for message in consumer:
            msg = message.value
            
            if "event_name" in msg:
                Incident.objects.create(
                    timestamp=datetime.now(),
                    camera=msg["device_info"]["IP"],
                    event=msg["event_name"],
                    incident=msg["msg"],
                    link="your_link",
                )
            elif "msg_type" in msg:
                ZoneStats.objects.create(
                    timestamp=datetime.now(),
                    camera=msg["device_info"]["IP"],
                    location=msg["zone_id"],
                    change=msg["msg"]["in"] - msg["msg"]["out"],
                )
