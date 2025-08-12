from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'lifelog'}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documents = db.relationship('Document', backref='user', lazy=True)
    projects = db.relationship('Project', backref='user', lazy=True)
    people = db.relationship('Person', backref='user', lazy=True)
    decisions = db.relationship('Decision', backref='user', lazy=True)
    chunks = db.relationship('Chunk', backref='user', lazy=True)

    def to_dict(self):
        return {"id": self.id, "email": self.email, "name": self.name, "created_at": self.created_at.isoformat()}
