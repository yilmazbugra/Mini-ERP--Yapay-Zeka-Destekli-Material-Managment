#!/usr/bin/env python3
"""
Veritabanındaki enum değerlerini düzeltir
"""

from app import create_app, db
from app.models import SalesOrder, PurchaseOrder

def fix_enum_values():
    """Enum değerlerini düzelt"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Enum değerleri düzeltiliyor...")
        
        # SalesOrder status değerlerini düzelt
        print("📝 Satış siparişleri düzeltiliyor...")
        sales_orders = db.session.query(SalesOrder).all()
        
        for order in sales_orders:
            if order.status == 'Approved':
                order.status = 'APPROVED'
            elif order.status == 'PartiallyShipped':
                order.status = 'PARTIALLY_SHIPPED'
            elif order.status == 'Closed':
                order.status = 'CLOSED'
        
        # PurchaseOrder status değerlerini düzelt
        print("📝 Satın alma siparişleri düzeltiliyor...")
        purchase_orders = db.session.query(PurchaseOrder).all()
        
        for order in purchase_orders:
            if order.status == 'Draft':
                order.status = 'DRAFT'
            elif order.status == 'Approved':
                order.status = 'APPROVED'
            elif order.status == 'PartiallyReceived':
                order.status = 'PARTIALLY_RECEIVED'
            elif order.status == 'Closed':
                order.status = 'CLOSED'
        
        db.session.commit()
        print("✅ Enum değerleri başarıyla düzeltildi!")
        
        # İstatistikler
        print(f"📊 Düzeltilen satış siparişleri: {len(sales_orders)}")
        print(f"📊 Düzeltilen satın alma siparişleri: {len(purchase_orders)}")

if __name__ == "__main__":
    fix_enum_values()
