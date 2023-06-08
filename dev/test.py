import asyncio
from app.database.legacy import connection as legacy_connection, models as legacy
from app.database.lightning import connection as lightning_connection, models as lightning
from app.helper import managed_workspace

SEPARATOR = "***"


async def main():
    if not legacy_connection.database.is_connected:
        await legacy_connection.database.connect()
    if not lightning_connection.database.is_connected:
        await lightning_connection.database.connect()

    controller = await legacy.Controller.get_by_cid(1505592)
    await managed_workspace.configure_for_controller(controller)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
coroutine = main()
loop.run_until_complete(coroutine)
