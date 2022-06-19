from ast import And
import sys
from datetime import datetime
sys.path.insert(0,"..")
from database.timescaledb import TimescaleDB


class ReadSIMCardUsage(TimescaleDB):
    def __init__(self, json_encoders = {}):
        # Parent class ctor feeding
        super().__init__('usage', json_encoders)

    def select_organizations_table(self):
        query_select_organizations_table = f"SELECT id, org_id FROM organizations;"
        return self.execute_sql_query_fetch_all_json(query_select_organizations_table)

    def select_simcards_table(self):
        query_select_simcards_table = f"""SELECT simcards.id, sim_card_id, org_id FROM simcards
                                            INNER JOIN organizations ON
                                            simcards.id_org = organizations.id;"""
        return self.execute_sql_query_fetch_all_json(query_select_simcards_table)

    def select_organization_table(self, org_id):
        query_select_organizations_table = f"""SELECT id, org_id FROM organizations
                                                Where org_id like '{org_id}';"""
        return self.execute_sql_query_fetch_one_json(query_select_organizations_table)

    def select_simcard_table(self, sim_card_id):
        query_select_organizations_table = f"""SELECT simcards.id, sim_card_id, org_id
                                                FROM simcards
                                                INNER JOIN organizations ON
                                                simcards.id_org = organizations.id
                                                Where sim_card_id like '{sim_card_id}';"""
        print(query_select_organizations_table)
        return self.execute_sql_query_fetch_one_json(query_select_organizations_table)

    def __build_select_simcard_usage_query(self, sim_card_id, start, end, every):
        if start == end:
                start = datetime.combine(start, datetime.min.time())
                end = datetime.combine(end, datetime.max.time())

        query = f"""SELECT time_bucket('{every}', time) AS date, SUM(bytes_used) AS bytes_used_total
                    FROM simcard_usage
                    INNER JOIN simcards ON
                    simcard_usage.id_sim_card = simcards.id
                    Where sim_card_id like '{sim_card_id}'
                    AND time >= '{start}' AND time < '{end}'
                    GROUP BY date
                    ORDER BY date;"""
        return query

    def select_simcard_usage_hypertable(self, sim_card_id, start, end, every):
        query_select_usage_table = self.__build_select_simcard_usage_query(sim_card_id, start, end, every)
        return self.execute_sql_query_fetch_all_json(query_select_usage_table)

    def __build_select_organization_usage_query(self, org_id, start, end, every):
        if start == end:
                start = datetime.combine(start, datetime.min.time())
                end = datetime.combine(end, datetime.max.time())

        query = f"""SELECT time_bucket('{every}', time) AS date, SUM(bytes_used) AS bytes_used_total
                    FROM simcard_usage
                    NATURAL JOIN organizations
                    NATURAL JOIN simcards
                    WHERE org_id like '{org_id}'
                    AND time >= '{start}' AND time < '{end}'
                    GROUP BY date
                    ORDER BY date;"""
        return query

    def select_organization_usage_hypertable(self, org_id, start, end, every):
        query_select_usage_table = self.__build_select_organization_usage_query(org_id, start, end, every)
        return self.execute_sql_query_fetch_all_json(query_select_usage_table)