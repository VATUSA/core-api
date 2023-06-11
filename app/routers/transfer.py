import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from app import auth, constants
from app.database.legacy import models as legacy
from app.helper import action_log
from vatusa_core import models


router = APIRouter(
    prefix="/transfer",
    tags=["core/transfer"],
    dependencies=[],
)


@router.get('/pending/{facility_id}', response_model=list[models.Transfer])
@router.get('/pending', response_model=list[legacy.Transfer])
async def get_pending_transfers(facility_id: Optional[str] = None, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.TRANSFER)
    query = legacy.Transfer.query().filter(legacy.Transfer.status == 0)
    if facility_id is not None:
        query.filter(legacy.Transfer.to == facility_id)
    transfers: list[legacy.Transfer] = await query.all()
    return [transfer.to_response_model() for transfer in transfers]


@router.get('/controller/{cid}', response_model=list[models.Transfer])
async def get_controller_transfers(cid: int, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.TRANSFER)
    transfers: list[legacy.Transfer] = await legacy.Transfer.query().filter(cid=cid).all()
    return [transfer.to_response_model() for transfer in transfers]


@router.post('/', response_model=models.Transfer)
async def create_transfer(data: models.CreateTransferRequest, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRANSFER)
    controller: legacy.Controller = await legacy.Controller.get_by_cid(data.cid)
    submitted_by_controller: legacy.Controller = await legacy.Controller.get_by_cid(data.submitted_by_cid)
    holds: list[legacy.TransferHold] = await legacy.TransferHold.active_by_cid(data.cid)
    if data.force and data.submitted_by_cid != 0:
        raise HTTPException(409, "Only automatic transfers can be forced!")
    if len(holds) > 0 and not data.force:
        raise HTTPException(409, f'CID {data.cid} has holds which prevent this transfer!')
    pending_transfers_count = await legacy.Transfer.objects.filter(legacy.Transfer.status == 0).filter(cid=data.cid).count()
    if pending_transfers_count > 0:
        raise HTTPException(409, f'CID {data.cid} has pending transfers which prevent this transfer!')
    transfer: legacy.Transfer = legacy.Transfer(
        cid=controller,
        to=data.facility,
        from_=controller.facility,
        reason=data.reason,
        status=0,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    await transfer.save()
    if data.force:
        transfer.status = 1
        controller.facility = transfer.to
        controller.facility_join = datetime.datetime.now()
        await transfer.update()
        await controller.update()
        await action_log.log(data.cid, f'Automatic transfer from {transfer.from_} to {transfer.to}: {transfer.reason}')
    else:
        if data.submitted_by_cid != data.cid:
            await action_log.log(data.cid,
                                 f'[Submitted by {submitted_by_controller.fname} {submitted_by_controller.lname}]'
                                 f' Requested transfer from {transfer.from_} to {transfer.to}: {transfer.reason}')
        else:
            await action_log.log(data.cid,
                                 f'Requested transfer from {transfer.from_} to {transfer.to}: {transfer.reason}')
        # TODO: Send Email to Controller
        # TODO: Send email to Staff (vatusa2, old atm+datm, new atm+datm)
        pass
    return transfer.to_response_model()


@router.get('/{transfer_id}', response_model=models.Transfer)
async def get_transfer(transfer_id: int, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.TRANSFER)
    transfer: legacy.Transfer = await legacy.Transfer.query().filter(id=transfer_id).get_or_none()
    return transfer.to_response_model()


@router.put('/{transfer_id}')
async def process_transfer(transfer_id: int,
                           data: models.ProcessTransferRequest,
                           api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRANSFER)
    transfer: legacy.Transfer = await legacy.Transfer.query().filter(id=transfer_id).get_or_none()
    if transfer is None:
        raise HTTPException(404, "Transfer record not found")
    if transfer.status != 0:
        raise HTTPException(400, "Transfer is not pending")

    controller: legacy.Controller = await legacy.Controller.get_by_cid(transfer.cid.cid)
    admin_controller: legacy.Controller = await legacy.Controller.get_by_cid(data.admin_cid)
    if admin_controller is None:
        raise Exception(400, "admin_cid is required and must be valid")
    if data.approve is True:
        controller.facility = transfer.to
        controller.facility_join = datetime.datetime.now()
        await controller.save()
        transfer.status = 1
        await action_log.log(controller.cid,
                             f'Transfer from {transfer.from_} to {transfer.to} approved by '
                             f'{admin_controller.fname} {admin_controller.lname}')
        # TODO: transfer approved notification
    else:
        transfer.status = 2
        await action_log.log(controller.cid,
                             f'Transfer from {transfer.from_} to {transfer.to} rejected by '
                             f'{admin_controller.fname} {admin_controller.lname}')
        # TODO: transfer rejected notification
    transfer.actionby = data.admin_cid
    transfer.actiontext = data.reason
    transfer.updated_at = datetime.datetime.now()
    await transfer.save()
    return transfer.to_response_model()


@router.get('/hold/controller/{cid}', response_model=list[models.TransferHold])
async def get_controller_active_holds(cid: int, api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_read(auth.PermissionObject.TRANSFER_HOLD)
    holds: list[legacy.TransferHold] = await legacy.TransferHold.active_by_cid(cid)
    return [hold.to_response_model() for hold in holds]


@router.post('/hold')
async def create_transfer_hold(data: models.CreateTransferHoldRequest,
                               api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRANSFER_HOLD)
    controller: legacy.Controller = await legacy.Controller.get_by_cid(data.cid)
    hold = legacy.TransferHold(
        controller=data.cid,
        hold=data.hold,
        start_date=data.start_date,
        end_date=data.end_date,
        created_by_cid=data.created_by_cid
    )
    await hold.save()
    await controller.update_restriction_flags()
    if data.created_by_cid is not None:
        created_by_controller: legacy.Controller = await legacy.Controller.objects.filter(cid=data.created_by_cid).first()
        await action_log.log(data.cid, f'Hold {hold.hold} added (start: {hold.start_date} - end: {hold.end_date}) '
                                       f'by {created_by_controller.fname} {created_by_controller.lname}')
    await action_log.log(data.cid, f'Hold {hold.hold} added (start: {hold.start_date} - end: {hold.end_date})')


@router.put('/hold/{hold_id}')
async def update_transfer_hold(hold_id: int,
                               data: models.UpdateTransferHoldRequest,
                               api_key: auth.APIKey = Depends(auth.get_api_key)):
    api_key.assert_can_write(auth.PermissionObject.TRANSFER_HOLD)
    hold: legacy.TransferHold = legacy.TransferHold.objects.filter(id=hold_id).first()
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
    controller: legacy.Controller = await legacy.Controller.get_by_cid(hold.controller.cid)
    await controller.update_restriction_flags()
    if data.admin_cid is not None:
        admin_controller: legacy.Controller = legacy.Controller.objects.filter(cid=data.admin_cid).first()
        await action_log.log(hold.controller.cid, f'Hold {hold.hold} modified: {", ".join(log_parts)} '
                                              f'by {admin_controller.fname} {admin_controller.lname}')
    else:
        await action_log.log(hold.controller.cid, f'Hold {hold.hold} modified: {", ".join(log_parts)} ')


