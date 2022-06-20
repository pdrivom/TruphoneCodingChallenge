
import sqlalchemy
from sqlalchemy import ForeignKey
from database.timescale_alchemy import AlchemyTimescaleDB


class Metadata(AlchemyTimescaleDB):
    def __init__(self):
        super().__init__('usage')

    def create_metadata(self):

        self.inventory = sqlalchemy.Table(
            "inventory",
            self.metadata,
            sqlalchemy.Column("sim_card_id", sqlalchemy.String, primary_key=True),
            sqlalchemy.Column("org_id", sqlalchemy.String),
        )

        self.usage = sqlalchemy.Table(
            "usage",
            self.metadata,
            sqlalchemy.Column("date", sqlalchemy.DateTime, primary_key=True, nullable=False),
            sqlalchemy.Column("bytes_used", sqlalchemy.Integer),
            sqlalchemy.Column("sim_card_id", sqlalchemy.String, ForeignKey("inventory.sim_card_id"), nullable=False),
        )

        super().create_metadata()

    async def populate(self):

        query = self.inventory.select()
        inventory = await self.database.fetch_all(query)
        if len(inventory) == 0:
            query = self.inventory.insert()
            values = [
                    { "sim_card_id": "89440001", "org_id": "a01b7" },
                    { "sim_card_id": "89440002", "org_id": "a01b7" },
                    { "sim_card_id": "89440003", "org_id": "a01b7" },
                    { "sim_card_id": "89440004", "org_id": "a01b7" },
                    { "sim_card_id": "89440005", "org_id": "a01b7" },
                    { "sim_card_id": "89440006", "org_id": "x00g8" },
                    { "sim_card_id": "89440007", "org_id": "x00g8" },
                    { "sim_card_id": "89440008", "org_id": "x00g8" },
                    { "sim_card_id": "89440009", "org_id": "x00g8" },
                    { "sim_card_id": "89440010", "org_id": "x00g8" },
                    { "sim_card_id": "89440011", "org_id": "f00ff" },
                    { "sim_card_id": "89440012", "org_id": "f00ff" },
                    { "sim_card_id": "89440013", "org_id": "f00ff" },
                    { "sim_card_id": "89440014", "org_id": "f00ff" },
                    { "sim_card_id": "89440016", "org_id": "f00ff" }
                    ]
            await self.database.execute_many(query=query, values=values)
