import os
import json
from kafka import KafkaConsumer


class KafkaTopicConsumer(object):
    # Object to handle kafka consumer events and run a function on each event
    def __init__(self, topic):
        self.server = os.environ['KAFKA_BOOTSTRAP_SERVERS']
        self.topic = topic

    def start_consuming(self, action):
        # starts the async KafkaConsumer and on new message, run a given function
        self.consumer = KafkaConsumer(self.topic,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        bootstrap_servers="kafka:9092",
        auto_offset_reset='earliest',
        enable_auto_commit=True,)

        print(f"Consuming from topic {self.topic} on server {self.server}")

        try:
            for message in self.consumer:
                if message.topic == self.topic:
                    action(message.value)
        except Exception as e:
            print(e)
