import psycopg2
from psycopg2.extras import execute_values
import os


class JsonEncoder():

    def __init__(self, json_encoders):
        self.json_encoders = json_encoders

    def encode(self, data):
        if type(data) not in self.json_encoders:
            return data
        return self.json_encoders[type(data)](data)

class LoggableObject(object):
    def log_and_solve_error(self, e):
        # Logging can be managed here
        print(e)

class TimescaleDB(LoggableObject):
    def __init__(self, dbname, json_encoders = {}):
        # Timescale configs loaded from env. variables
        user = os.environ['POSTGRES_USER']
        password = os.environ['POSTGRES_PASSWORD']
        host = os.environ['POSTGRES_HOST']
        port = os.environ['POSTGRES_PORT']
        self.CONNECTION = f"postgres://{user}:{password}@{host}:{port}/{dbname}"
        print(f"TimescaleDB connection string: {self.CONNECTION}")
        self.encoder = JsonEncoder(json_encoders)

    def connect(self):
        # Connects to TimescaleDB
        try:
            self.conn = psycopg2.connect(self.CONNECTION)
            print(f"Connected to TimescaleDB [{self.CONNECTION}]")
        except psycopg2.Error as e:
            print(e.pgerror)

    def execute_sql_statement(self, statements):
        # Executes a list of statements then commits the changes
        try:
            cursor = self.conn.cursor()
            for statement in statements:
                cursor.execute(statement)
            self.conn.commit()
            cursor.close()
        except Exception as e:
            self.log_and_solve_error(e)

    def execute_sql_query_fetch_all(self, query):
        # Gets all records returned by query
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            insert = cursor.fetchall()
            cursor.close()
            return insert
        except psycopg2.Error as e:
            print(e.pgerror)

    def execute_sql_query_fetch_one(self, query):
        # Gets first record returned by query
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            data = cursor.fetchone()
            cursor.close()
            return data
        except psycopg2.Error as e:
            print(e.pgerror)
            return None

    def execute_sql_query_fetch_all_json(self, query):
        # Gets all records returned by query in json format
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            r = [dict((cursor.description[i][0],self.encoder.encode(value)) \
                    for i, value in enumerate(row)) for row in cursor.fetchall()]
            cursor.close()
            return r
        except Exception as e:
            self.log_and_solve_error(e)
            return None

    def execute_sql_query_fetch_one_json(self, query):
        # Gets first record returned by query in json format
        try:
            r = self.execute_sql_query_fetch_all_json(query)
            return (r[0] if r else None)
        except Exception as e:
            self.log_and_solve_error(e)
            return None

    def __build_select_exist_query(self, table):
        # Builds a query to check table existence
        return f"""SELECT EXISTS (
                    SELECT FROM
                    pg_tables
                    WHERE
                    schemaname = 'public' AND
                    tablename  = '{table}'
                    );"""

    def check_table_exists(self, tablename):
        return self.execute_sql_query_fetch_one(self.__build_select_exist_query(tablename))[0]

    def execute_sql_statement_batch(self, statement, batch):
        cursor = self.conn.cursor()
        execute_values(cursor, statement, batch)
        self.conn.commit()
        cursor.close()
