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

class SIMCardUsage(TimescaleDB):
    def __init__(self):
        super().__init__('usage')

    def onboarding(self):
        if not self.__create_organizations_table() and not self.__create_simcards_table():
            self.__initialize_inventory()
            self.__create_usage_hypertable()

        print('Onboarding finished.')

    def __create_organizations_table(self):
        exists = self.check_table_exists('organizations')
        if not exists:
            query_create_organizations_table = "CREATE TABLE organizations (id SERIAL PRIMARY KEY, org_id VARCHAR(8));"
            self.execute_sql_statement([query_create_organizations_table])
        return exists

    def __create_simcards_table(self):
        exists = self.check_table_exists('simcards')
        if not exists:
            query_create_simcards_table = """CREATE TABLE simcards (
                                                    id SERIAL PRIMARY KEY,
                                                    sim_card_id VARCHAR(16),
                                                    org_id INTEGER,
                                                    FOREIGN KEY (org_id) REFERENCES organizations (id)
                                                    );"""
            self.execute_sql_statement([query_create_simcards_table])
        return exists

    def __create_usage_hypertable(self):
        exists = self.check_table_exists('simcard_usage')
        if not exists:
            query_create_usage_table = """CREATE TABLE simcard_usage (
                                            time TIMESTAMPTZ NOT NULL,
                                            sim_card_id INTEGER,
                                            bytes_used INTEGER,
                                            FOREIGN KEY (sim_card_id) REFERENCES simcards (id)
                                            );"""
            query_create_usage_hypertable = "SELECT create_hypertable('simcard_usage', 'time');"
            self.execute_sql_statement([query_create_usage_table, query_create_usage_hypertable])

    def __initialize_inventory(self):
        try:
            orgs = set()
            sims = []
            for card in inventory:
                org = card['org-id']
                sim = card['sim-card-id']
                orgs.add(f"INSERT INTO organizations (org_id) VALUES ('{org}');")
                id_org = f"(SELECT id from organizations WHERE org_id='{org}')"
                sims.append(f"INSERT INTO simcards (sim_card_id,org_id) VALUES ('{sim}',{id_org});")
            self.execute_sql_statement(orgs)
            self.execute_sql_statement(sims)
        except Exception as e:
            self.log_and_solve_error(e)


class KafkaTopicConsumer(LoggableObject):
    def __init__(self, topic):
        self.server = os.environ['KAFKA_BOOTSTRAP_SERVERS']
        self.topic = topic

    def start_consuming(self, action):
        self.consumer = KafkaConsumer(self.topic,value_deserializer=lambda m: json.loads(m.decode('utf-8')),bootstrap_servers="kafka:9092")
        print(f"Consuming from topic {self.topic} on server {self.server}")

        try:
            for message in self.consumer:
                if message.topic == self.topic:
                    action(message.value)
        except Exception as e:
            self.log_and_solve_error(e)


class KafkaTopicToTimescaleDb(SIMCardUsage, KafkaTopicConsumer):

    current_batch = []

    def __init__(self, topic):
        SIMCardUsage.__init__(self)
        KafkaTopicConsumer.__init__(self, topic)
        self.MAX_BATCH_SIZE = int(os.environ['MAX_BATCH_SIZE'])
        self.connect()
        self.onboarding()

    def start_bridging(self):
        self.start_consuming(self.__process_insert_simcard_usage_hypertable)

    def __insert_simcard_usage_hypertable(self, time, sim_card_id, bytes_used):
        if self.__validate_datetime(time):
            insert = f"""INSERT INTO simcard_usage (time,sim_card_id,bytes_used)
                            VALUES ('{time}',
                            (SELECT id from simcards WHERE sim_card_id='{sim_card_id}'),
                            '{bytes_used}');"""
            self.current_batch.append(insert)
            print(self.MAX_BATCH_SIZE)
            print(len(self.current_batch))
            if len(self.current_batch) >= self.MAX_BATCH_SIZE:
                self.execute_sql_statement(self.current_batch)
                self.current_batch = []

    def __process_insert_simcard_usage_hypertable(self, message):
        self.__insert_simcard_usage_hypertable(message['date'],message['sim-card-id'], message['bytes-used'])

    def __validate_datetime(self, datetime):
        try:
            parser.parse(datetime)
            return True
        except Exception as e:
            return False


bridge = KafkaTopicToTimescaleDb('usage')
bridge.start_bridging()


