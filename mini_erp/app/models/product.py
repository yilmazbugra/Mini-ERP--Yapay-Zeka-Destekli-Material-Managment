from app.models.base import BaseModel
from app import db

class Product(BaseModel):
    __tablename__ = 'products'
    
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(20), nullable=False)  # adet, kg, m, etc.
    barcode = db.Column(db.String(100), unique=True, nullable=True)
    reorder_point = db.Column(db.Integer, default=0, nullable=False)
    safety_stock = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    stock_movements = db.relationship('StockMovement', backref='product', lazy='dynamic')
    inventory_balances = db.relationship('InventoryBalance', backref='product', lazy='dynamic')
    purchase_order_lines = db.relationship('PurchaseOrderLine', backref='product', lazy='dynamic')
    sales_order_lines = db.relationship('SalesOrderLine', backref='product', lazy='dynamic')
    reorder_rules = db.relationship('ReorderRule', backref='product', lazy='dynamic')





