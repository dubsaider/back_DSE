from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
import json
from datetime import datetime
from api.models import Incident, ZoneStat, CameraStat, Camera


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

        aggregated_data = {}
        last_second = None

        for message in consumer:
            msg = message.value
            
            if "event_name" in msg:
                # TODO read incident
                Incident.objects.create(
                    timestamp=datetime.now(),
                    camera=msg["device_info"]["IP"],
                    event=msg["event_name"],
                    incident=msg["msg"],
                    link="your_link", # TODO save video   
                )
            elif "line_id" in msg:
                msg_parts = msg.split()
                date, time, _, _, camera_ip, _, line_id, _, zone_id, _, zone, _, in_count, _, out_count, _, direction = msg_parts
                timestamp = f"{date}T{time[:8]}Z"
                aggregation_key = f"{camera_ip}_{timestamp}"

                current_second = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                if last_second is None or current_second > last_second:
                    for data in aggregated_data.values():
                        camera = Camera.objects.get(camera_ip=data['camera_ip'])
                        CameraStat.objects.create(
                            timestamp=current_second,
                            camera=camera,
                            input_value=data['input_value'],
                            output_value=data['output_value'],
                        )
                    aggregated_data = {}
                    last_second = current_second

                if aggregation_key not in aggregated_data:
                    aggregated_data[aggregation_key] = {
                        'timestamp': timestamp,
                        'camera_ip': camera_ip,
                        'input_value':   1 if direction == 'in' else   0,
                        'output_value':   0 if direction == 'in' else   1,
                    }
                else:
                    aggregated_data[aggregation_key]['input_value'] +=   1 if direction == 'in' else   0
                    aggregated_data[aggregation_key]['output_value'] +=   0 if direction == 'in' else   1

        for data in aggregated_data.values():
            camera = Camera.objects.get(camera_ip=data['camera_ip'])
            CameraStat.objects.create(
                timestamp=current_second,
                camera=camera,
                input_value=data['input_value'],
                output_value=data['output_value'],
            )
