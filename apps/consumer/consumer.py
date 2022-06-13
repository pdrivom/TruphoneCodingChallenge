import os
import json
from kafka import KafkaConsumer
import psycopg2
from dateutil import parser

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

class LoggableObject(object):
    def log_and_solve_error(self, e):
        if e is psycopg2.Error:
            cursor = self.conn.cursor()
            cursor.execute("ROLLBACK")
            self.conn.commit()
            cursor.close()
        print(e)

class TimescaleDB(LoggableObject):
    def __init__(self, dbname):
        user = os.environ['POSTGRES_USER']
        password = os.environ['POSTGRES_PASSWORD']
        host = os.environ['POSTGRES_HOST']
        port = os.environ['POSTGRES_PORT']
        self.CONNECTION = f"postgres://{user}:{password}@{host}:{port}/{dbname}"
        print(f"TimescaleDB connection string: {self.CONNECTION}")

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.CONNECTION)
            print(f"Connected to TimescaleDB [{self.CONNECTION}]")
        except psycopg2.Error as e:
            print(e.pgerror)

    def execute_sql_statement(self, queries):
        try:
            cursor = self.conn.cursor()
            for query in queries:
                cursor.execute(query)
            self.conn.commit()
            cursor.close()
        except Exception as e:
            self.log_and_solve_error(e)

    def execute_sql_query_fetch_all(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        except psycopg2.Error as e:
            print(e.pgerror)

    def execute_sql_query_fetch_one(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            data = cursor.fetchone()
            cursor.close()
            return data
        except psycopg2.Error as e:
            print(e.pgerror)

    def __build_select_exist_query(self, table):
        return f"""SELECT EXISTS (
                    SELECT FROM
                    pg_tables
                    WHERE
                    schemaname = 'public' AND
                    tablename  = '{table}'
                    );"""

    def check_table_exists(self, tablename):
        return self.execute_sql_query_fetch_one(self.__build_select_exist_query(tablename))[0]


class SIMCardUsage(TimescaleDB, LoggableObject):
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
            query_create_organizations_table = "CREATE TABLE simcards (id SERIAL PRIMARY KEY, sim_card_id VARCHAR(16));"
            self.execute_sql_statement([query_create_organizations_table])
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
                orgs.add(f"INSERT INTO organizations (org_id) VALUES ('{card['org-id']}');")
                sims.append(f"INSERT INTO simcards (sim_card_id) VALUES ('{card['sim-card-id']}');")
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
    def __init__(self, topic):
        SIMCardUsage.__init__(self)
        KafkaTopicConsumer.__init__(self, topic)
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
            self.execute_sql_statement([insert])

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


