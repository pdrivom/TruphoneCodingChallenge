from datetime import date, datetime
from typing import List
import re
from fastapi import FastAPI, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from pydantic import BaseModel, Field, validator
from lib.timescale_read_usage import TimescaleReadUsage


class Inventory(BaseModel):
    sim_card_id: str
    org_id: str

class Bytes_Used(BaseModel):

    date: str
    bytes_used_total: int = Field(alias="bytes-used-total")

    class Config:
        allow_population_by_field_name = True

def validate_parameter_every(every):
    pattern = r'(\dhour|\dday)'
    result = re.match(pattern, every)
    return False if result is None else True

def validate_request(every):
    if not every:
        raise HTTPException(status_code=422, detail= "Query parameter 'every' cannot be empty. (ex: 1day / 1hour)")
    else:
        if not validate_parameter_every(every):
            raise HTTPException(status_code=422, detail= f"Query parameter 'every' cannot be {every}. (ex: 1day / 1hour)")

def convert_datetime_to_iso_8601(datetime: datetime):
        return datetime.strftime('%Y-%m-%d:%H:%M:%S')

app = FastAPI()
timescale = TimescaleReadUsage({datetime:convert_datetime_to_iso_8601})


@app.on_event("startup")
async def startup():
    await timescale.database.connect()
    timescale.create_metadata()
    await timescale.populate()

@app.on_event("shutdown")
async def shutdown():
    await timescale.database.disconnect()

@app.get("/api/v1/inventory", response_model=Page[Inventory])
async def read_inventory(page: int = 1, size: int = 50):
    # returns simcard inventory
    inventory = await timescale.select_inventory()
    return paginate(inventory)

def __read_organization(org_id: str):
    # checks the organization existence
    org = timescale.select_organization(org_id)
    if org is None:
        raise HTTPException(status_code=404, detail= f"No organization {org_id} found!")
    return org

def __read_simcard(sim_card_id: str):
    # checks the simcard existence
    sim = timescale.select_simcard(sim_card_id)
    if sim is None:
        raise HTTPException(status_code=404, detail= f"No simcard {sim_card_id} found!")
    return sim

@app.get("/api/v1/simcard/{sim_card_id}/usage", response_model=Page[Bytes_Used])
async def read_simcard_usage(sim_card_id: str, start: date, end: date, every: str, page: int = 1, size: int = 50):
    # validates checks the simcard existence. If Ok returns usage
    validate_request(every)
    __read_simcard(sim_card_id)
    usage = timescale.select_simcard_usage(sim_card_id, start, end, every)
    return paginate(usage)

@app.get("/api/v1/organization/{org_id}/usage", response_model=Page[Bytes_Used])
async def read_organization_usage(org_id: str, start: date, end: date, every: str, page: int = 1, size: int = 50):
    # validates checks the organization existence. If Ok returns usage
    validate_request(every)
    __read_organization(org_id)
    usage = timescale.select_organization_usage(org_id, start, end, every)
    return paginate(usage)


add_pagination(app)