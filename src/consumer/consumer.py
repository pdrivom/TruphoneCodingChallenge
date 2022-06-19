import json
import os

from dateutil import parser
from kafka import KafkaConsumer

import sys
sys.path.insert(0,"..")
from database.timescaledb import TimescaleDB, LoggableObject

inventory = [
{ "sim-card-id": "89440001", "org-id": "a01b7" },
{ "sim-card-id": "89440002", "org-id": "a01b7" },
{ "sim-card-id": "89440003", "org-id": "a01b7" },
{ "sim-card-id": "89440004", "org-id": "a01b7" },
{ "sim-card-id": "89440005", "org-id": "a01b7" },
{ "sim-card-id": "89440006", "org-id": "x00g8" },
{ "sim-card-id": "89440007", "org-id": "x00g8" },
{ "sim-card-id": "89440008", "org-id": "x00g8" },
{ "sim-card-id": "89440009", "org-id": "x00g8" },
{ "sim-card-id": "89440010", "org-id": "x00g8" },
{ "sim-card-id": "89440011", "org-id": "f00ff" },
{ "sim-card-id": "89440012", "org-id": "f00ff" },
{ "sim-card-id": "89440013", "org-id": "f00ff" },
{ "sim-card-id": "89440014", "org-id": "f00ff" },
{ "sim-card-id": "89440016", "org-id": "f00ff" }
]

class SaveSIMCardUsage(TimescaleDB):
    # Object to save on the TimescaleDB the orgs, simcards and usage
    def __init__(self):
        # Parent class ctor feeding
        super().__init__('usage')

    def onboarding(self):
        # Calls the Create and populate of the organizations and simcard tables and also simcard_usage hypertable
        if not self.__create_organizations_table() and not self.__create_simcards_table():
            self.__insert_inventory_tables()
            self.__create_usage_hypertable()

        print('Onboarding finished.')

    def __create_organizations_table(self):
        # Creates organizations table
        exists = self.check_table_exists('organizations')
        if not exists:
            query_create_organizations_table = "CREATE TABLE organizations (id SERIAL PRIMARY KEY, org_id VARCHAR(8));"
            self.execute_sql_statement([query_create_organizations_table])
        return exists

    def __create_simcards_table(self):
        # Creates simcards table
        exists = self.check_table_exists('simcards')
        if not exists:
            query_create_simcards_table = """CREATE TABLE simcards (
                                                    id SERIAL PRIMARY KEY,
                                                    sim_card_id VARCHAR(16),
                                                    id_org INTEGER,
                                                    FOREIGN KEY (id_org) REFERENCES organizations (id)
                                                    );"""
            self.execute_sql_statement([query_create_simcards_table])
        return exists

    def __create_usage_hypertable(self):
        # Creates simcard_usage hypertable
        exists = self.check_table_exists('simcard_usage')
        if not exists:
            query_create_usage_table = """CREATE TABLE simcard_usage (
                                            time TIMESTAMPTZ NOT NULL,
                                            id_sim_card INTEGER,
                                            bytes_used INTEGER,
                                            FOREIGN KEY (id_sim_card) REFERENCES simcards (id)
                                            );"""
            query_create_usage_hypertable = "SELECT create_hypertable('simcard_usage', 'time');"
            self.execute_sql_statement([query_create_usage_table, query_create_usage_hypertable])

    def __insert_inventory_tables(self):
        # Populates of the organizations and simcard tables
        try:
            orgs = set()
            sims = []
            for card in inventory:
                org = card['org-id']
                sim = card['sim-card-id']
                orgs.add(f"INSERT INTO organizations (org_id) VALUES ('{org}');")
                id_org = f"(SELECT id from organizations WHERE org_id='{org}')"
                sims.append(f"INSERT INTO simcards (sim_card_id,id_org) VALUES ('{sim}',{id_org});")
            self.execute_sql_statement(orgs)
            self.execute_sql_statement(sims)
        except Exception as e:
            self.log_and_solve_error(e)

class KafkaTopicConsumer(LoggableObject):
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
            self.log_and_solve_error(e)

class KafkaTopicToTimescaleDb(SaveSIMCardUsage, KafkaTopicConsumer):
    # Object to bridge the data from KafkaConsumer to TimescaleDB
    current_batch = []

    def __init__(self, topic):
        # Connect to Kafka and TimescaleDB
        SaveSIMCardUsage.__init__(self)
        KafkaTopicConsumer.__init__(self, topic)
        self.MAX_BATCH_SIZE = int(os.environ['MAX_BATCH_SIZE']) # Batch size to buffer before saving into the database
        self.connect()
        self.onboarding()

    def start_bridging(self):
        # Starts consuming from Kafka and executes the function that saves on de database
        self.start_consuming(self.__process_insert_simcard_usage_hypertable)

    def __insert_simcard_usage_hypertable(self, time, sim_card_id, bytes_used):
        # Validates the time stamp and inserts record into the hypertable
        if self.__validate_datetime(time):
            insert = f"""INSERT INTO simcard_usage (time,id_sim_card,bytes_used)
                            VALUES ('{time}',
                            (SELECT id from simcards WHERE sim_card_id='{sim_card_id}'),
                            '{bytes_used}');"""
            self.current_batch.append(insert)
            if len(self.current_batch) >= self.MAX_BATCH_SIZE:
                self.execute_sql_statement(self.current_batch)
                self.current_batch = []
                print('Batch inserted!')

    def __process_insert_simcard_usage_hypertable(self, message):
        # Json file from Kafka topic property splitting
        self.__insert_simcard_usage_hypertable(message['date'],message['sim-card-id'], message['bytes-used'])

    def __validate_datetime(self, datetime):
        # Validates if the timestamp makes sense
        try:
            parser.parse(datetime)
            return True
        except Exception as e:
            return False


bridge = KafkaTopicToTimescaleDb('usage')
bridge.start_bridging()


