from app.models.base import BaseModel
from app import db
from enum import Enum

class MovementDirection(Enum):
    IN = 'IN'
    OUT = 'OUT'

class MovementType(Enum):
    PURCHASE = 'Purchase'
    SALES = 'Sales'
    TRANSFER = 'Transfer'
    ADJUSTMENT = 'Adjustment'

class StockMovement(BaseModel):
    __tablename__ = 'stock_movements'
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    direction = db.Column(db.Enum(MovementDirection), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.Enum(MovementType), nullable=False)
    ref_document_no = db.Column(db.String(100), nullable=True)
    ref_line_id = db.Column(db.Integer, nullable=True)
    note = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='stock_movements')





