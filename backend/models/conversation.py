from . import db
from datetime import datetime

SenderType = db.Enum('user', 'ai', name='sender_type')

class Conversation(db.Model):
    __tablename__ = 'conversations'
    __table_args__ = {'schema': 'lifelog'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thread_id = db.Column(db.String, nullable=False)
    message = db.Column(db.Text, nullable=False)
    sender = db.Column(SenderType, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return { "id": self.id, "user_id": self.user_id, "thread_id": self.thread_id, "message": self.message, "sender": self.sender, "date": self.date.isoformat() if self.date else None }
