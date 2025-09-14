from app.models.base import BaseModel
from app import db

class Supplier(BaseModel):
    __tablename__ = 'suppliers'
    
    name = db.Column(db.String(200), nullable=False)
    tax_no = db.Column(db.String(20), unique=True, nullable=True)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy='dynamic')
    reorder_rules = db.relationship('ReorderRule', backref='supplier', lazy='dynamic')





