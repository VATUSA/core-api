import datetime
from typing import Optional, Annotated
import pydantic
from fastapi import APIRouter, Depends, HTTPException

from app import auth
from app.database.legacy import models as legacy
from app.database.lightning import models as lightning
from app.helper import action_log


router = APIRouter(
    prefix="/transfer",
    tags=["core/transfer"],
    dependencies=[],
)


@router.get('/pending/{facility_id}', response_model=list[legacy.Transfer])
@router.get('/pending', response_model=list[legacy.Transfer])
async def get_pending_transfers(facility_id: Optional[str] = None, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.TRANSFER)
    query = legacy.Transfer.objects.filter(legacy.Transfer.status == 0)
    if facility_id is not None:
        query.filter(legacy.Transfer.to == facility_id)
    transfers: list[legacy.Transfer] = await query.all()
    return transfers


@router.get('/controller/{cid}', response_model=list[legacy.Transfer])
async def get_controller_transfers(cid: int, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.TRANSFER)
    transfers: list[legacy.Transfer] = await legacy.Transfer.objects.filter(cid=cid).all()
    return transfers


class CreateTransferRequest(pydantic.BaseModel):
    cid: int
    facility: str
    reason: str
    submitted_by_cid: int


@router.post('/')
async def create_transfer(data: CreateTransferRequest, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRANSFER)
    controller: legacy.Controller = legacy.Controller.objects.filter(cid=data.cid).first()
    submitted_by_controller: legacy.Controller = legacy.Controller.objects.filter(cid=data.submitted_by_cid).first()
    holds: list[lightning.TransferHold] = await lightning.TransferHold.active_by_cid(data.cid)
    if len(holds) > 0:
        raise HTTPException(409, f'CID {data.cid} has holds which prevent this transfer!')
    transfer: legacy.Transfer = legacy.Transfer(
        cid=data.cid,
        to=data.facility,
        from_=controller.facility,
        reason=data.reason,
        status=0,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    await transfer.save()
    if data.submitted_by_cid != data.cid:
        await action_log.log(data.cid, f'[Submitted by {submitted_by_controller.fname} {submitted_by_controller.lname}]'
                                       f' Requested transfer from {transfer.from_} to {transfer.to}: {transfer.reason}')
    else:
        await action_log.log(data.cid, f'Requested transfer from {transfer.from_} to {transfer.to}: {transfer.reason}')


@router.get('/hold/controller/{cid}', response_model=list[lightning.TransferHold])
async def get_controller_active_holds(cid: int, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.TRANSFER_HOLD)
    holds: list[lightning.TransferHold] = await lightning.TransferHold.active_by_cid(cid)
    return holds


class CreateTransferHoldRequest(pydantic.BaseModel):
    cid: int
    hold: str
    start_date: Optional[datetime.datetime]
    end_date: Optional[datetime.datetime]
    created_by_cid: Optional[int]


@router.post('/hold')
async def create_transfer_hold(data: CreateTransferHoldRequest, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRANSFER_HOLD)
    hold = lightning.TransferHold(
        controller=data.cid,
        hold=data.hold,
        start_date=data.start_date,
        end_date=data.end_date,
        created_by_cid=data.created_by_cid
    )
    created_by_controller: legacy.Controller = await legacy.Controller.objects.filter(cid=data.created_by_cid).first()
    await hold.save()
    if created_by_controller is not None:
        await action_log.log(data.cid, f'Hold {hold.hold} added (start: {hold.start_date} - end: {hold.end_date}) '
                                       f'by {created_by_controller.fname} {created_by_controller.lname}')
    await action_log.log(data.cid, f'Hold {hold.hold} added (start: {hold.start_date} - end: {hold.end_date})')


class UpdateTransferHoldRequest(pydantic.BaseModel):
    end_date: Optional[datetime.datetime] = None
    clear_end_date: Optional[bool] = False
    is_released: Optional[bool] = None
    admin_cid: Optional[int] = None


@router.put('/hold/{hold_id}')
async def update_transfer_hold(hold_id: int,
                               data: UpdateTransferHoldRequest,
                               api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRANSFER_HOLD)
    hold: lightning.TransferHold = lightning.TransferHold.objects.filter(id=hold_id).first()
    log_parts = []
    if data.clear_end_date:
        log_parts.append(f'end_date {hold.end_date} => None')
        hold.end_date = None
    elif data.end_date:
        log_parts.append(f'end_date {hold.end_date} => {data.end_date}')
        hold.end_date = data.end_date
    if data.is_released is not None:
        log_parts.append(f'is_released {hold.is_released} => {data.is_released}')
        hold.is_released = data.is_released
        if data.admin_cid is not None:
            hold.released_by_cid = data.admin_cid
    await hold.save()
    if data.admin_cid is not None:
        admin_controller: legacy.Controller = legacy.Controller.objects.filter(cid=data.admin_cid).first()
        await action_log.log(hold.controller, f'Hold {hold.hold} modified: {", ".join(log_parts)} '
                                              f'by {admin_controller.fname} {admin_controller.lname}')
    else:
        await action_log.log(hold.controller, f'Hold {hold.hold} modified: {", ".join(log_parts)} ')


