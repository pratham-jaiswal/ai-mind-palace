from models import Conversation
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class ConversationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Conversation
        load_instance = True
