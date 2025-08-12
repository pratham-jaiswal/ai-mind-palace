from . import db
from datetime import datetime

class Person(db.Model):
    __tablename__ = 'people'
    __table_args__ = {'schema': 'lifelog'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    additional_info = db.Column(db.JSON, nullable=True)
    last_mentioned = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "name": self.name, "notes": self.notes, "last_mentioned": self.last_mentioned.isoformat()}