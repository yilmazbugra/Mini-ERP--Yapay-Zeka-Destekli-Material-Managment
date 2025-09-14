from app.models.base import BaseModel
from app import db

class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'
    
    entity = db.Column(db.String(50), nullable=False)  # Table name
    entity_id = db.Column(db.Integer, nullable=False)  # Record ID
    action = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    diff_json = db.Column(db.Text, nullable=True)  # JSON diff of changes
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')





