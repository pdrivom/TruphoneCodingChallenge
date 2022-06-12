import json
from kafka import KafkaConsumer


print('Starting consumer..')

consumer = KafkaConsumer(
    'usage',
    bootstrap_servers="kafka:9092",
)

print('Consuming from topic "usage" on server kafka:9092')

for message in consumer:
    print(message)