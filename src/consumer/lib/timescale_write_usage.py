import psycopg2
from psycopg2.extras import execute_values
import sys
sys.path.insert(0,"..")
from database.metadata import Metadata



class TimescaleWriteUsage(Metadata):
    # Object to save on the TimescaleDB the orgs, simcards and usage
    def __init__(self):
        # Parent class ctor feeding
        super().__init__()

    def connect(self):
        # Connects to TimescaleDB
        try:
            self.conn = psycopg2.connect(self.DATABASE_URL)
            print(f"Connected to TimescaleDB [{self.DATABASE_URL}]")
        except psycopg2.Error as e:
            print(e.pgerror)

    def build_insert_into_usage(self, date, bytes_used, sim_card_id):
        # builds sql statement to insert into usage table
        insert = f"""INSERT INTO usage (date,bytes_used,sim_card_id)
            VALUES ('{date}','{bytes_used}',{sim_card_id});"""
        return insert

    def execute_sql_statement_batch(self, statements):
        # executes a list o sql statements
        # ToDo: proper batching should be implemented
        try:
            cursor = self.conn.cursor()
            for statement in statements:
                cursor.execute(statement)
            self.conn.commit()
            cursor.close()
        except Exception as e:
            print(e)

