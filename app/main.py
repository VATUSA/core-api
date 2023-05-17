from fastapi import FastAPI
from app.common import middleware
from app.database.legacy import connection as legacy_connection
from app.database.lightning import connection as lightning_connection
from .routers import academy, controller, info, roster, solo, training_record, transfer

app = FastAPI()

# app.add_middleware(middleware.HelperPreCacheMiddleware)

app.include_router(academy.router)
app.include_router(info.router)
app.include_router(roster.router)


legacy_connection.attach(app)
lightning_connection.attach(app)


@app.get("/")
async def root():
    return {"message": "VATUSA Core API"}
