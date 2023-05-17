import ormar
from .connection import database
from .connection import metadata


class BaseMeta(ormar.ModelMeta):
    database = database
    metadata = metadata
