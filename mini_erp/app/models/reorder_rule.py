from app.models.base import BaseModel
from app import db

class ReorderRule(BaseModel):
    __tablename__ = 'reorder_rules'
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    moq = db.Column(db.Integer, nullable=False)  # Minimum Order Quantity
    lead_time_days = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Unique constraint on product_id + supplier_id
    __table_args__ = (db.UniqueConstraint('product_id', 'supplier_id', name='_product_supplier_uc'),)





