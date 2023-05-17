import ormar
from .connection import database, metadata


class BaseMeta(ormar.ModelMeta):
    database = database
    metadata = metadata
