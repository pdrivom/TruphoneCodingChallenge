import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.insert(0,"..")
from database.timescaledb import TimescaleDB


class Organization(BaseModel):
    id: str
    org_id: str

class SIM_Card(BaseModel):
    id: str
    sim_card_id: str
    org_id: str

class Bytes_Used(BaseModel):
    id: str
    title: str

class ReadSIMCardUsage(TimescaleDB):
    def __init__(self):
        # Parent class ctor feeding
        super().__init__('usage')

    def select_organizations_table(self, org_id):
        query_select_organizations_table = f"""SELECT id, org_id FROM organizations
                                                Where org_id like '{org_id}';"""
        return self.execute_sql_query_fetch_all_json(query_select_organizations_table)

    def execute_sql_query_fetch_all_json(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            r = [dict((cursor.description[i][0], value) \
                    for i, value in enumerate(row)) for row in cursor.fetchall()]
            cursor.close()
            print(r)
            return r
        except Exception as e:
            self.log_and_solve_error(e)

app = FastAPI()


db = ReadSIMCardUsage()
db.connect()


@app.get("/api/v1/organization/{org_id}", response_model=Organization)
async def read_main(org_id: str):
    try:
        org = db.select_organizations_table(org_id)
        print(org)
        return org
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
