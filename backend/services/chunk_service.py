from .base_service import BaseService
from models.chunk import Chunk

class ChunkService(BaseService):
    model = Chunk
