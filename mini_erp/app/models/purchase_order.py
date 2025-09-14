from app.models.base import BaseModel
from app import db
from enum import Enum

class PurchaseOrderStatus(Enum):
    DRAFT = 'Draft'
    APPROVED = 'Approved'
    PARTIALLY_RECEIVED = 'PartiallyReceived'
    CLOSED = 'Closed'

class PurchaseOrder(BaseModel):
    __tablename__ = 'purchase_orders'
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT, nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    expected_date = db.Column(db.Date, nullable=True)
    note = db.Column(db.Text, nullable=True)
    
    # Relationships
    lines = db.relationship('PurchaseOrderLine', backref='purchase_order', lazy='dynamic', cascade='all, delete-orphan')

class PurchaseOrderLine(BaseModel):
    __tablename__ = 'purchase_order_lines'
    
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    received_qty = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Received, Closed





