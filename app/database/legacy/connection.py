import logging
import os
import dotenv
import databases
import sqlalchemy

dotenv.load_dotenv()

database_user = os.getenv("LEGACY_DATABASE_USER")
database_password = os.getenv("LEGACY_DATABASE_PASSWORD")
database_host = os.getenv("LEGACY_DATABASE_HOST")
database_port = os.getenv("LEGACY_DATABASE_PORT")
database_database = os.getenv("LEGACY_DATABASE_DATABASE")

CONNECTION_STRING = \
    f"mysql+pymysql://{database_user}:{database_password}@{database_host}:{database_port}/{database_database}"

metadata = sqlalchemy.MetaData()
database = databases.Database(CONNECTION_STRING, )

logging.basicConfig()


# logging.getLogger("databases").setLevel(logging.DEBUG)

def attach(app):
    @app.on_event("startup")
    async def startup() -> None:
        if not database.is_connected:
            await database.connect()

    @app.on_event("shutdown")
    async def shutdown() -> None:
        if database.is_connected:
            await database.disconnect()
