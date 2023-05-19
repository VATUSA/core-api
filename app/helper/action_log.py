import datetime

from app.database.legacy import models as legacy


async def log(cid: int, message: str, admin_cid: int = 0):
    log_rec = legacy.ActionLog(
        to=cid,
        from_=admin_cid,
        log=message,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    await log_rec.save()
