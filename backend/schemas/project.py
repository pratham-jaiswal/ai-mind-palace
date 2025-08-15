from models import Project
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class ProjectSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        load_instance = True
