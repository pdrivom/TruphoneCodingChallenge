from datetime import datetime
import sys
import psycopg2
sys.path.insert(0,"..")
from database.metadata import Metadata


class JsonEncoder():

    def __init__(self, json_encoders):
        self.json_encoders = json_encoders

    def encode(self, data):
        if type(data) not in self.json_encoders:
            return data
        return self.json_encoders[type(data)](data)

class TimescaleReadUsage(Metadata):
    def __init__(self, json_encoders = {}):
        super().__init__()
        self.encoder = JsonEncoder(json_encoders)

    def convert_datetime_to_iso_8601(datetime: datetime):
        return datetime.strftime('%Y-%m-%d:%H:%M:%S')

    def select_inventory(self):
        query = self.inventory.select()
        return self.database.fetch_all(query)

    def select_organization(self, org_id):
        query = f"SELECT org_id FROM inventory WHERE org_id like '{org_id}';"
        return self.execute_sql_query_fetch_one(query)

    def select_simcard(self, sim_card_id):
        query = f"SELECT org_id FROM inventory WHERE sim_card_id like '{sim_card_id}';"
        return self.execute_sql_query_fetch_one(query)

    def connect_sync(self):
        # Connects to TimescaleDB
        try:
            self.conn = psycopg2.connect(self.DATABASE_URL)
            print(f"Connected to TimescaleDB [{self.DATABASE_URL}]")
        except psycopg2.Error as e:
            print(e.pgerror)

    def execute_sql_query_fetch_all(self, query):
        # Gets all records returned by query
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            r = [dict((cursor.description[i][0],self.encoder.encode(value)) \
                    for i, value in enumerate(row)) for row in cursor.fetchall()]
            cursor.close()
            return r
        except Exception as e:
            print(e)

    def execute_sql_query_fetch_one(self, query):
        # Gets first record returned by query in json format
        try:
            r = self.execute_sql_query_fetch_all(query)
            return (r[0] if r else None)
        except Exception as e:
            print(e)
            return None

    def select_simcard_usage(self,sim_card_id, start, end, every):
        keys = ['date', 'bytes_used_total']
        query = f"""SELECT time_bucket('{every}', date) AS date, SUM(bytes_used) AS bytes_used_total
                    FROM usage
                    Where sim_card_id like '{sim_card_id}'
                    AND date >= '{start}' AND date < '{end}'
                    GROUP BY date
                    ORDER BY date;"""
        return self.execute_sql_query_fetch_all(query)
        #return [dict(zip(keys, l)) for l in usage ]


    def select_organization_usage(self, org_id, start, end, every):
        keys = ['date', 'bytes_used_total']
        query = f"""
            WITH t AS (SELECT time_bucket('{every}', date) AS date, SUM(bytes_used) AS bytes_used_total
            FROM usage
            INNER JOIN inventory ON
            usage.sim_card_id = inventory.sim_card_id
            WHERE inventory.org_id like '{org_id}'
            AND date >= '{start}' AND date < '{end}'
            GROUP BY date ORDER BY date)
            SELECT date, SUM(bytes_used_total) AS bytes_used_total
            FROM t
            GROUP BY date;
            """
        return self.execute_sql_query_fetch_all(query)
        #return [dict(zip(keys, l)) for (l) in usage ]