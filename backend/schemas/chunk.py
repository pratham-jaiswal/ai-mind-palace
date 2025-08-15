from models import ma, Chunk

class ChunkSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Chunk
        load_instance = True
