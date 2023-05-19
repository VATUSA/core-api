from fastapi import APIRouter
from app.routers.training import record


router = APIRouter(
    prefix="/training",
    tags=[],
    dependencies=[],
)

router.include_router(record.router)
