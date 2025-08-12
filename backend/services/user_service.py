from .base_service import BaseService
from models.user import User

class UserService(BaseService):
    model = User
