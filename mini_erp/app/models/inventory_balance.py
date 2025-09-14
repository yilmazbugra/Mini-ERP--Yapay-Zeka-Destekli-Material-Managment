from app.models.base import BaseModel
from app import db

class InventoryBalance(BaseModel):
    __tablename__ = 'inventory_balances'
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    on_hand_qty = db.Column(db.Integer, default=0, nullable=False)
    reserved_qty = db.Column(db.Integer, default=0, nullable=False)
    available_qty = db.Column(db.Integer, default=0, nullable=False)
    
    # Unique constraint on product_id + warehouse_id
    __table_args__ = (db.UniqueConstraint('product_id', 'warehouse_id', name='_product_warehouse_uc'),)
    
    @property
    def available_qty_calculated(self):
        """Calculate available quantity (on_hand - reserved)"""
        return max(0, self.on_hand_qty - self.reserved_qty)
    
    def update_available_qty(self):
        """Update available quantity based on on_hand and reserved"""
        self.available_qty = self.available_qty_calculated





