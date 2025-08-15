from models import Person
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class PersonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        load_instance = True
