from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
import json
import datetime
from api.models import Incident, ZoneStats, CameraStats, Camera


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

        for message in consumer:
            msg = message.value
            
            if "event_name" in msg:
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
                timestamp = f"{date}T{time}Z"
                second_key = f"{timestamp[:19]}Z"
                direction_key = f"{camera_ip}_{direction}"
                if direction_key not in aggregated_data:
                    aggregated_data[direction_key] = {
                        'timestamp': second_key,
                        'camera_ip': camera_ip,
                        'direction': direction,
                        'input_value':  1 if direction == 'in' else  0,
                        'output_value':  0 if direction == 'in' else  1,
                    }
                else:
                    aggregated_data[direction_key]['input_value'] +=  1 if direction == 'in' else  0
                    aggregated_data[direction_key]['output_value'] +=  0 if direction == 'in' else  1

                if datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') != second_key:
                    for data in aggregated_data.values():
                        camera = Camera.objects.get(camera_ip=data['camera_ip'])
                        CameraStats.objects.create(
                            timestamp=datetime.datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%SZ"),
                            camera=camera,
                            input_value=data['input_value'],
                            output_value=data['output_value'],
                        )
                    aggregated_data = {}
            elif "msg_type" in msg:
                ZoneStats.objects.create(
                    timestamp=datetime.now(),
                    camera=msg["device_info"]["IP"],
                    location=msg["zone_id"],
                    change=msg["msg"]["in"] - msg["msg"]["out"],
                )

        for data in aggregated_data.values():
            camera = Camera.objects.get(camera_ip=data['camera_ip'])
            CameraStats.objects.create(
                timestamp=datetime.datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%SZ"),
                camera=camera,
                input_value=data['input_value'],
                output_value=data['output_value'],
            )