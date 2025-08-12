from . import db
from datetime import datetime

class Chunk(db.Model):
    __tablename__ = 'chunks'
    __table_args__ = {'schema': 'lifelog'}

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "document_id": self.document_id, "user_id": self.user_id, "text": self.text, "chunk_index": self.chunk_index, "created_at": self.created_at.isoformat()}
