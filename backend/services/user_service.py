from .base_service import BaseService
from models.user import User
from sqlalchemy import func, String

class UserService(BaseService):
    model = User

    @classmethod
    def update(cls, email, name, clerk_id):
        user = cls.get_by_clerk_id(clerk_id)
        if not user:
            return None
        user.email = email
        user.name = name
        cls.model.query.session.commit()
        return user
    
    @classmethod
    def delete(cls, clerk_id):
        user = cls.get_by_clerk_id(clerk_id)
        if not user:
            return False
        cls.model.query.session.delete(user)
        cls.model.query.session.commit()
        return True
    
    @classmethod
    def get_by_clerk_id(cls, clerk_id):
        return cls.model.query.filter(
            func.coalesce(
                cls.model.additional_info.op("->>")("clerk_id"), ''
            ) == clerk_id
        ).first()