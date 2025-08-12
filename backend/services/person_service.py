from .base_service import BaseService
from models.person import Person

class PersonService(BaseService):
    model = Person
