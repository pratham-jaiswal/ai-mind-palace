from models import Conversation
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

class ConversationSchema(SQLAlchemySchema):
    class Meta:
        model = Conversation
        load_instance = True

    role = auto_field("sender")
    content = auto_field("message")

class ConversationMetadataSchema(SQLAlchemySchema):
    class Meta:
        model = Conversation
        load_instance = True

    thread_id = auto_field()
    date = auto_field()
