from typing import Annotated
from fastapi import Depends, FastAPI
from app import auth, middleware
from app.database.legacy import connection as legacy_connection
from app.database.lightning import connection as lightning_connection
from app.routers import training, transfer
# from app.routers import academy, controller, info, roster, solo, training_record, transfer

app = FastAPI()

# app.add_middleware(middleware.HelperPreCacheMiddleware)

app.include_router(training.router)
app.include_router(transfer.router)


legacy_connection.attach(app)
lightning_connection.attach(app)


@app.get("/")
async def root():
    return {"message": "VATUSA Core API"}
