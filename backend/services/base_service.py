from models import db

class BaseService:
    model = None

    @classmethod
    def create(cls, **kwargs):
        obj = cls.model(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def get(cls, obj_id):
        return cls.model.query.get(obj_id)

    @classmethod
    def list(cls, user_id=None, limit=100, offset=0):
        q = cls.model.query
        if user_id:
            q = q.filter_by(user_id=user_id)
        # return q.offset(offset).limit(limit).all()
        return q.offset(offset).all()

    @classmethod
    def update(cls, obj_id, **kwargs):
        obj = cls.get(obj_id)
        if not obj:
            return None
        for k, v in kwargs.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.session.commit()
        return obj

    @classmethod
    def delete(cls, obj_id):
        obj = cls.get(obj_id)
        if not obj:
            return False
        db.session.delete(obj)
        db.session.commit()
        return True
