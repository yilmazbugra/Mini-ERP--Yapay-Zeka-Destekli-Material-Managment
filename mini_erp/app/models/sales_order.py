from app.models.base import BaseModel
from app import db
from enum import Enum

class SalesOrderStatus(Enum):
    DRAFT = 'Draft'
    APPROVED = 'Approved'
    PARTIALLY_SHIPPED = 'PartiallyShipped'
    CLOSED = 'Closed'

class SalesOrder(BaseModel):
    __tablename__ = 'sales_orders'
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Enum(SalesOrderStatus), default=SalesOrderStatus.DRAFT, nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    expected_ship_date = db.Column(db.Date, nullable=True)
    note = db.Column(db.Text, nullable=True)
    
    # Relationships
    lines = db.relationship('SalesOrderLine', backref='sales_order', lazy='dynamic', cascade='all, delete-orphan')

class SalesOrderLine(BaseModel):
    __tablename__ = 'sales_order_lines'
    
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    shipped_qty = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Shipped, Closed





