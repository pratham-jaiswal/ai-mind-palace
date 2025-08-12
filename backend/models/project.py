from . import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'projects'
    __table_args__ = {'schema': 'lifelog'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(512), nullable=False)
    status = db.Column(db.String(64), default='idea')
    description = db.Column(db.Text, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "title": self.title, "status": self.status, "description": self.description, "last_updated": self.last_updated.isoformat()}
