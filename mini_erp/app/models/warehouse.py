from app.models.base import BaseModel
from app import db

class Warehouse(BaseModel):
    __tablename__ = 'warehouses'
    
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    stock_movements = db.relationship('StockMovement', backref='warehouse', lazy='dynamic')
    inventory_balances = db.relationship('InventoryBalance', backref='warehouse', lazy='dynamic')





