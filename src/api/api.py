from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.insert(0,"..")
from database.timescaledb import TimescaleDB


fake_db = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
}

db = TimescaleDB('usage')


app = FastAPI()


class Item(BaseModel):
    id: str
    title: str
    description: Union[str, None] = None


@app.get("/items/{item_id}", response_model=Item)
async def read_main(item_id: str):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    if item.id in fake_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    fake_db[item.id] = item
    return item