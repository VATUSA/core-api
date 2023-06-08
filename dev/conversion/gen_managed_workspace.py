import asyncio
import math

from app.database.legacy import connection as legacy_connection, models as legacy
from app.database.lightning import connection as lightning_connection, models as lightning
from app.helper import managed_workspace

SEPARATOR = "***"

PAGE_SIZE = 100


async def main():
    if not legacy_connection.database.is_connected:
        await legacy_connection.database.connect()
    if not lightning_connection.database.is_connected:
        await lightning_connection.database.connect()

    query = legacy.Controller.query().filter(flag_homecontroller=1)
    count: int = await query.count()
    pages: int = math.ceil(count / PAGE_SIZE)
    for i in range(1, pages+1):
        controllers: list[legacy.Controller] = await query.paginate(i, PAGE_SIZE).all()
        for controller in controllers:
            if managed_workspace.should_controller_have_account(controller):
                print(f'Creating account for CID {controller.cid}')
                await managed_workspace.configure_for_controller(controller)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
coroutine = main()
loop.run_until_complete(coroutine)
