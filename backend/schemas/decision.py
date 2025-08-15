from models import Decision
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class DecisionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Decision
        load_instance = True
