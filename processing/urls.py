from django.urls import path
from .views import (
    ObjectsDetectionLogList,
    start_kafka_consumer,
)

urlpatterns = [
    path('logs/', ObjectsDetectionLogList.as_view(), name='log-list'),
    path('start-kafka-consumer', start_kafka_consumer, name='start-kafka-consumer'),
]