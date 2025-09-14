#!/usr/bin/env python3
"""
Daha Fazla Sentetik Veri Üretici
AI modelleri için daha fazla veri üretir
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from app import create_app, db
from app.models import (
    SalesOrder, SalesOrderLine, Customer, Product
)
from app.models.sales_order import SalesOrderStatus

def generate_more_orders():
    """Daha fazla sipariş verisi üret"""
    
    app = create_app()
    with app.app_context():
        
        print("Daha fazla sipariş verisi üretiliyor...")
        
        # Mevcut verileri al
        customers = Customer.query.all()
        products = Product.query.all()
        
        if not customers or not products:
            print("Müşteri veya ürün bulunamadı!")
            return
        
        # Son 6 aylık veri üret (180 gün)
        start_date = datetime.now() - timedelta(days=180)
        
        for day in range(180):
            current_date = start_date + timedelta(days=day)
            
            # Günlük sipariş sayısı (1-8 arası, hafta sonları daha az)
            if current_date.weekday() in [5, 6]:  # Hafta sonu
                orders_per_day = random.randint(1, 4)
            elif current_date.weekday() == 0:  # Pazartesi
                orders_per_day = random.randint(3, 8)
            else:  # Diğer günler
                orders_per_day = random.randint(2, 6)
            
            for order_num in range(orders_per_day):
                # Sipariş oluştur
                customer = random.choice(customers)
                
                # Benzersiz sipariş numarası oluştur
                order_no = f"SO{current_date.strftime('%Y%m%d')}{order_num+1:03d}"
                counter = 1
                while SalesOrder.query.filter_by(order_no=order_no).first():
                    order_no = f"SO{current_date.strftime('%Y%m%d')}{order_num+1:03d}_{counter}"
                    counter += 1
                
                sales_order = SalesOrder(
                    customer_id=customer.id,
                    order_no=order_no,
                    status=random.choice(list(SalesOrderStatus)),
                    order_date=current_date.date(),
                    expected_ship_date=(current_date + timedelta(days=random.randint(1, 7))).date(),
                    note=f"Ek sipariş - {current_date.strftime('%d.%m.%Y')}"
                )
                db.session.add(sales_order)
                db.session.flush()  # ID'yi almak için
                
                # Sipariş satırları oluştur (1-5 satır)
                lines_count = random.randint(1, 5)
                for line_num in range(lines_count):
                    product = random.choice(products)
                    sales_line = SalesOrderLine(
                        sales_order_id=sales_order.id,
                        product_id=product.id,
                        qty=random.randint(1, 25),
                        unit_price=Decimal(str(round(random.uniform(10.0, 1000.0), 2))),
                        shipped_qty=random.randint(0, 25) if sales_order.status in [SalesOrderStatus.PARTIALLY_SHIPPED, SalesOrderStatus.CLOSED] else 0,
                        status=random.choice(['Pending', 'Shipped', 'Closed'])
                    )
                    db.session.add(sales_line)
        
        db.session.commit()
        
        # Sonuçları göster
        total_orders = SalesOrder.query.count()
        print(f"Toplam sipariş sayısı: {total_orders}")
        print("Ek sipariş verileri başarıyla eklendi!")

if __name__ == "__main__":
    generate_more_orders()
