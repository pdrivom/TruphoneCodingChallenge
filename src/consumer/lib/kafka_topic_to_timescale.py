import os
from dateutil import parser
from sqlalchemy  import text
from lib.kafka_consumer_usage import KafkaTopicConsumer
from lib.timescale_write_usage import TimescaleWriteUsage

class KafkaTopicToTimescaleDb(TimescaleWriteUsage, KafkaTopicConsumer):
    # Object to bridge the data from KafkaConsumer to TimescaleDB
    current_batch = []

    def __init__(self, topic):
        # Connect to Kafka and TimescaleDB
        TimescaleWriteUsage.__init__(self)
        KafkaTopicConsumer.__init__(self, topic)
        self.MAX_BATCH_SIZE = int(os.environ['MAX_BATCH_SIZE']) # Batch size to buffer before saving into the database

    def start_bridging(self):
        # Starts consuming from Kafka and executes the function that saves on de database
        self.start_consuming(self.__process_insert_simcard_usage_hypertable)

    def __insert_simcard_usage_hypertable(self, message):
        # Validates the time stamp and inserts record into the hypertable
        if self.__validate_datetime(message['date']):
            self.current_batch.append(
                self.build_insert_into_usage(
                    message['date'],
                    message['bytes-used'],
                    message['sim-card-id']
                )
            )
            if len(self.current_batch) >= self.MAX_BATCH_SIZE:
                self.execute_sql_statement_batch(self.current_batch)
                self.current_batch = []
                print('Batch inserted!')

    def __process_insert_simcard_usage_hypertable(self, message):
        # Json file from Kafka topic property splitting
        self.__insert_simcard_usage_hypertable(message)

    def __validate_datetime(self, datetime):
        # Validates if the timestamp makes sense
        try:
            parser.parse(datetime)
            return True
        except Exception as e:
            return False
