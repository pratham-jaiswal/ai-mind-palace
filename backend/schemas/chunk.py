from models import Chunk
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class ChunkSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Chunk
        load_instance = True
