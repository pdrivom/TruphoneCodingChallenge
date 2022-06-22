import os
import databases
import sqlalchemy


class AlchemyTimescaleDB(object):
    def __init__(self, dbname):
        # Timescale configs loaded from env. variables

        user = os.environ['POSTGRES_USER']
        password = os.environ['POSTGRES_PASSWORD']
        host = os.environ['POSTGRES_HOST']
        port = os.environ['POSTGRES_PORT']
        self.DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        print(f"TimescaleDB connection string: {self.DATABASE_URL}")
        self.database = databases.Database(self.DATABASE_URL)
        self.metadata = sqlalchemy.MetaData()
        self.engine = sqlalchemy.create_engine(self.DATABASE_URL)
        self.metadata.create_all(self.engine)

    def create_metadata(self):
        # creates metadata using sqlalchemy
        self.metadata.create_all(self.engine)
