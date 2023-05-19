import datetime
from typing import Optional, Annotated
import pydantic
from fastapi import APIRouter, Depends, HTTPException

from app import auth, models
from app.database.legacy import models as legacy
from app.database.lightning import models as lightning
from app.helper import action_log


router = APIRouter(
    prefix="/record",
    tags=["core/training/record"],
    dependencies=[],
)


@router.get('/facility/{facility}', response_model=list[models.TrainingRecord])
async def get_facility_training_records(facility: str, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.TRAINING_RECORD)
    pass


@router.get('/controller/{cid}', response_model=list[models.TrainingRecord])
async def get_controller_training_records(facility: str, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.TRAINING_RECORD)
    pass


@router.post('/')
async def create_training_record(api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRAINING_RECORD)
    pass


@router.put('/{record_id}')
async def update_training_record(api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRAINING_RECORD)
    pass


@router.delete('/{record_id}')
async def delete_training_record(api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRAINING_RECORD)
    pass
