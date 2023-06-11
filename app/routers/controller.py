import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from app import auth, constants
from app.database.legacy import models as legacy
from app.helper import action_log
from vatusa_core import models


router = APIRouter(
    prefix="/controller",
    tags=["core/controller"],
    dependencies=[],
)


@router.get('/{cid}', response_model=models.Controller)
async def get_controller(cid: int, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.CONTROLLER)
    controller = await legacy.Controller.get_by_cid(cid)
    return controller.to_response_model()
