from dotenv import load_dotenv
import enum
import os
from fastapi import Header, HTTPException
from typing import Optional
from app.database.lightning import models as lightning

load_dotenv()

API_KEY_MIN_LENGTH = 20


class PermissionObject(enum.Enum):
    TRAINING_RECORD = 'training_record'
    TRANSFER = 'transfer'
    TRANSFER_HOLD = 'transfer_hold'


class APIKey:
    token: lightning.CoreAPIToken
    permissions_map: dict[str, lightning.CoreAPITokenPermission]

    def __init__(
            self,
            rec: lightning.CoreAPIToken
    ):
        if not rec.enabled:
            raise HTTPException(403, "Token is not enabled")

        self.token = rec
        self.permissions_map = {p.object: p for p in rec.permissions}

    def can_write(self, obj: PermissionObject) -> bool:
        return self.token.can_write_all or self.permissions_map.get(obj.value).can_write

    def assert_can_write(self, obj: PermissionObject):
        if not self.can_write(obj):
            raise Exception(403, "Write Operation Not Authorized")

    def can_read(self, obj: PermissionObject) -> bool:
        return self.token.can_read_all or self.permissions_map.get(obj.value).can_read

    def assert_can_read(self, obj: PermissionObject):
        if not self.can_read(obj):
            raise Exception(403, "Read Operation Not Authorized")


async def get_api_key(api_key_header: Optional[str] = Header(None, alias='Authorization')):
    if api_key_header is None:
        raise HTTPException(401, "No Authorization Token")
    key_type, key_value = api_key_header.split(' ')
    if key_type != 'Token':
        raise HTTPException(401, "Invalid Authorization Format")

    rec: lightning.CoreAPIToken = await lightning.CoreAPIToken.objects\
        .select_related(lightning.CoreAPIToken.permissions)\
        .filter(token=key_value)\
        .get_or_none()

    if rec is None:
        raise HTTPException(403, "Invalid Token")

    if not rec.enabled:
        raise HTTPException(403, "Token is not enabled")

    return APIKey(rec)

