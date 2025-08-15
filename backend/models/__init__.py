from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

from .user import User
from .document import Document
from .project import Project
from .person import Person
from .decision import Decision
from .chunk import Chunk
from .conversation import Conversation