from datetime import date, datetime, timezone
from typing import List
import re
from fastapi import FastAPI, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from pydantic import BaseModel, Field, validator
from lib.read_simcard_usage import ReadSIMCardUsage


class Organization(BaseModel):
    id: str
    org_id: str

class SIM_Card(BaseModel):
    id: str
    sim_card_id: str
    org_id: str

class Bytes_Used(BaseModel):
    bytes_used_total: int = Field(alias="bytes-used-total")
    date:str

    class Config:
        allow_population_by_field_name = True

def convert_datetime_to_iso_8601(datetime: datetime):
        return datetime.strftime('%Y-%m-%d:%H:%M:%S')

def validate_parameter_every(every):
    pattern = '(\dhour|\dday)'
    result = re.match(pattern, every)
    return False if result is None else True

def validate_and_respond(every, usage):
    if not every:
        raise HTTPException(status_code=422, detail= "Query parameter 'every' cannot be empty. (ex: 1day / 1hour)")
    else:
        if validate_parameter_every(every):
            return paginate(usage)
        else:
            raise HTTPException(status_code=422, detail= f"Query parameter 'every' cannot be {every}. (ex: 1day / 1hour)")

app = FastAPI()
db = ReadSIMCardUsage({datetime:convert_datetime_to_iso_8601})
db.connect()


@app.get("/api/v1/organizations", response_model=List[Organization])
async def read_organizations():
    orgs = db.select_organizations_table()
    if len(orgs) <= 1:
        raise HTTPException(status_code=404, detail="No organizations found!")
    return orgs

@app.get("/api/v1/simcards", response_model=Page[SIM_Card])
async def read_simcards():
    sim = db.select_simcards_table()
    if sim is None:
        raise HTTPException(status_code=404, detail= f"No simcards found!")
    return paginate(sim)

@app.get("/api/v1/organization/{org_id}", response_model=Organization)
async def read_organization(org_id: str):
    org = db.select_organization_table(org_id)
    if org is None:
        print(org)
        raise HTTPException(status_code=404, detail= f"No organization {org_id} found!")
    return org

@app.get("/api/v1/simcard/{sim_card_id}", response_model=SIM_Card)
async def read_simcard(sim_card_id: str):
    sim = db.select_simcard_table(sim_card_id)
    if sim is None:
        raise HTTPException(status_code=404, detail= f"No simcard {sim_card_id} found!")
    return sim

@app.get("/api/v1/simcard/{sim_card_id}/usage", response_model=Page[Bytes_Used])
async def read_simcard_usage(sim_card_id: str, start: date, end: date, every: str, page: int = 1, size: int = 50):
    return validate_and_respond(every, db.select_simcard_usage_hypertable(sim_card_id, start, end, every))


@app.get("/api/v1/organization/{org_id}/usage", response_model=Page[Bytes_Used])
async def read_organization_usage(org_id: str, start: date, end: date, every: str, page: int = 1, size: int = 50):
    return validate_and_respond(every, db.select_organization_usage_hypertable(org_id, start, end, every))


add_pagination(app)