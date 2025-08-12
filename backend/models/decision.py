from . import db
from datetime import datetime

class Decision(db.Model):
    __tablename__ = 'decisions'
    __table_args__ = {'schema': 'lifelog'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    decision_text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "decision_text": self.decision_text, "date": self.date.isoformat()}
