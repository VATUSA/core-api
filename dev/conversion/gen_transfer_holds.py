import asyncio
import datetime
import logging
import os
import math
import dotenv
from app import constants
from app.database.legacy import connection, models as legacy
import vatusa_core
from vatusa_core import models

dotenv.load_dotenv()

log = logging.getLogger('gen_transfer_holds')
log.setLevel(logging.DEBUG)

PAGE_SIZE = 100

vatusa_core.set_url(os.environ.get('API_URL'))
vatusa_core.set_token(os.environ.get('API_TOKEN'))
vatusa_core.set_log_level(logging.DEBUG)


async def main():
    if not connection.database.is_connected:
        await connection.database.connect()
    query = legacy.Controller.query()
    count: int = await query.count()
    pages: int = math.ceil(count / PAGE_SIZE)
    for i in range(1, pages+1):
        controllers: list[legacy.Controller] = await legacy.Controller.query()\
            .filter(flag_homecontroller=1)\
            .filter(legacy.Controller.rating >= constants.rating.OBS)\
            .paginate(i, PAGE_SIZE).all()
        coroutines = []
        for controller in controllers:
            coroutines.append(process_holds(controller))
        await asyncio.gather(*coroutines)


async def process_holds(controller: legacy.Controller):
    log.debug(f'Processing CID {controller.cid}')
    calculated_holds: list[models.CreateTransferHoldRequest] = []

    # HOLD_OBS_ACADEMY
    if controller.rating == constants.rating.OBS and controller.flag_needbasic:
        calculated_holds.append((models.CreateTransferHoldRequest(
            cid=controller.cid,
            hold=constants.hold.HOLD_OBS_ACADEMY,
        )))

    # HOLD_RECENT_TRANSFER
    if controller.facility_join + datetime.timedelta(days=90) > datetime.datetime.now():
        calculated_holds.append((models.CreateTransferHoldRequest(
            cid=controller.cid,
            hold=constants.hold.HOLD_RECENT_TRANSFER,
        )))

    # HOLD_RECENT_PROMOTION
    if controller.last_promotion is not None \
            and controller.last_promotion + datetime.timedelta(days=90) > datetime.datetime.now():
        calculated_holds.append((models.CreateTransferHoldRequest(
            cid=controller.cid,
            hold=constants.hold.HOLD_RECENT_PROMOTION,
        )))

    # HOLD_PENDING_TRANSFER
    if True in [t.status == 0 for t in controller.transfers]:
        calculated_holds.append((models.CreateTransferHoldRequest(
            cid=controller.cid,
            hold=constants.hold.HOLD_PENDING_TRANSFER,
        )))

    # HOLD_RCE_REQUIRED
    if (
            (controller.rating > constants.rating.OBS and controller.flag_needbasic)
            or (controller.facility == 'ZAE' and
                controller.facility_join + datetime.timedelta(days=180) < datetime.datetime.now())
    ):
        calculated_holds.append((models.CreateTransferHoldRequest(
            cid=controller.cid,
            hold=constants.hold.HOLD_RCE_REQUIRED,
        )))

    if len(calculated_holds) > 0:
        await add_holds(controller.cid, calculated_holds)


async def add_holds(cid: int, requests: list[models.CreateTransferHoldRequest]):
    existing_holds: list[models.TransferHold] = \
        await vatusa_core.transfer.get_controller_active_holds(cid)
    existing_hold_ids = [hold.hold for hold in existing_holds]
    for request in requests:
        if request.hold not in existing_hold_ids:
            log.debug(f"Adding hold {request.hold} to CID {cid}")
            await vatusa_core.transfer.create_transfer_hold(request)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
coroutine = main()
loop.run_until_complete(coroutine)
