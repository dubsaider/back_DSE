import asyncio
import aiokafka
import re
from api.models import Camera, ObjectsDetectionLog, DetectedObjectType
from datetime import datetime


async def main():
    consumer = aiokafka.AIOKafkaConsumer(
        'cv_prod', # нужно написать топик который слушать
        bootstrap_servers=['10.61.38.13:9092', '10.61.38.13:9093', '10.61.38.13:9094'],
        )
    await consumer.start()
    try:
        async for msg in consumer:
            decode_msg = msg.value.decode('utf-8')

            data = decode_msg[:19]
            classes = decode_msg[29:]

            date_time = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            result = re.findall(r'[a-z]\w+: \d+', classes)

            print(decode_msg)
            for obj in result:
                class_name, amount = obj.split(': ')

                base_msg = ObjectsDetectionLog(
                    datestamp=date_time,
                    camera=Camera('name', 'ip', 'description'), # нужно дописать
                    type=DetectedObjectType(class_name),
                    count=int(amount)
                )
                print(base_msg)
                base_msg.save()

    finally:
        await consumer.stop()



if __name__ == '__main__':
    corutine = main()
    asyncio.run(corutine)