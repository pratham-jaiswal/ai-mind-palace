from . import db
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'documents'
    __table_args__ = {'schema': 'lifelog'}  

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(512), nullable=True)
    source = db.Column(db.String(128), nullable=True)
    text = db.Column(db.Text, nullable=True)
    additional_info = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chunks = db.relationship('Chunk', backref='document', lazy=True)

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "filename": self.filename, "source": self.source, "text": self.text, "created_at": self.created_at.isoformat()}
