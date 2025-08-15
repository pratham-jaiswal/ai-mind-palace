from models import Document
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class DocumentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Document
        load_instance = True
