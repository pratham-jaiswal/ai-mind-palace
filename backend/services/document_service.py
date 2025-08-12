from .base_service import BaseService
from models.document import Document

class DocumentService(BaseService):
    model = Document
