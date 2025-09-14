#!/usr/bin/env python3
"""
3 Aylık Sentetik ERP Veri Üretici
Bu script mevcut veri yapısını koruyarak 3 aylık gerçekçi sentetik veri üretir.
"""

import random
import string
from datetime import datetime, timedelta, date
from decimal import Decimal
from app import create_app, db
from app.models import (
    Customer, Product, Supplier, Warehouse, User, 
    SalesOrder, SalesOrderLine, PurchaseOrder, PurchaseOrderLine,
    StockMovement, InventoryBalance, ReorderRule, AuditLog
)
from app.models.sales_order import SalesOrderStatus
from app.models.purchase_order import PurchaseOrderStatus
from app.models.stock_movement import MovementDirection, MovementType

# Türkçe isimler ve şirket isimleri
TURKISH_NAMES = [
    "Ahmet Yılmaz", "Mehmet Demir", "Ayşe Kaya", "Fatma Özkan", "Ali Çelik",
    "Zeynep Arslan", "Mustafa Şahin", "Elif Doğan", "Hasan Yıldız", "Selin Öztürk",
    "Burak Kılıç", "Gamze Aydın", "Emre Çakır", "Seda Yılmaz", "Okan Özkan",
    "Pınar Demir", "Cem Kaya", "Derya Şahin", "Tolga Doğan", "Ebru Yıldız"
]

COMPANY_NAMES = [
    "ABC Teknoloji", "XYZ İnşaat", "DEF Gıda", "GHI Tekstil", "JKL Otomotiv",
    "MNO Elektronik", "PQR Kimya", "STU Mobilya", "VWX Enerji", "YZA Lojistik",
    "BCD Makine", "EFG Sağlık", "HIJ Eğitim", "KLM Turizm", "NOP Finans"
]

PRODUCT_CATEGORIES = [
    "Elektronik", "Gıda", "Tekstil", "Kozmetik", "Ev Eşyası", "Spor", 
    "Kitap", "Oyuncak", "Bahçe", "Otomotiv", "İnşaat", "Sağlık"
]

UNITS = ["adet", "kg", "m", "lt", "m²", "m³", "paket", "kutu", "düzine"]

def generate_random_string(length=8):
    """Rastgele string üret"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_phone():
    """Türkiye telefon numarası üret"""
    return f"0{random.randint(500, 599)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"

def generate_email(name):
    """Email adresi üret"""
    domains = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "company.com"]
    name_clean = name.lower().replace(" ", ".").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    return f"{name_clean}@{random.choice(domains)}"

def generate_tax_no():
    """Benzersiz vergi numarası üret"""
    while True:
        tax_no = f"{random.randint(1000000000, 9999999999)}"
        # Mevcut vergi numaralarını kontrol et (müşteri ve tedarikçi)
        existing_customer = Customer.query.filter_by(tax_no=tax_no).first()
        existing_supplier = Supplier.query.filter_by(tax_no=tax_no).first()
        if not existing_customer and not existing_supplier:
            return tax_no

def generate_barcode():
    """Benzersiz barkod üret"""
    while True:
        barcode = ''.join(random.choices(string.digits, k=13))
        # Mevcut barkodları kontrol et
        existing_barcode = Product.query.filter_by(barcode=barcode).first()
        if not existing_barcode:
            return barcode

def generate_sku():
    """Benzersiz SKU üret"""
    while True:
        sku = f"{random.choice(string.ascii_uppercase)}{random.randint(1000, 9999)}"
        # Mevcut SKU'ları kontrol et
        existing_sku = Product.query.filter_by(sku=sku).first()
        if not existing_sku:
            return sku

def generate_address():
    """Adres üret"""
    streets = ["Atatürk Caddesi", "Cumhuriyet Sokak", "İstiklal Caddesi", "Gazi Mustafa Kemal Bulvarı", "Fatih Sultan Mehmet Caddesi"]
    return f"{random.choice(streets)} No:{random.randint(1, 200)} {random.choice(['A', 'B', 'C'])} Blok Daire:{random.randint(1, 50)}"

def generate_synthetic_data():
    """3 aylık sentetik veri üret"""
    
    app = create_app()
    with app.app_context():
        
        print("3 aylık sentetik veri üretimi başlıyor...")
        
        # Mevcut verileri al
        existing_customers = Customer.query.all()
        existing_suppliers = Supplier.query.all()
        existing_products = Product.query.all()
        existing_warehouses = Warehouse.query.all()
        existing_users = User.query.all()
        
        print(f"Mevcut veriler: {len(existing_customers)} müşteri, {len(existing_suppliers)} tedarikçi, {len(existing_products)} ürün")
        
        # 1. Yeni müşteriler ekle (20 müşteri daha)
        print("Yeni müşteriler ekleniyor...")
        for i in range(20):
            customer = Customer(
                name=random.choice(COMPANY_NAMES),
                tax_no=generate_tax_no(),
                address=generate_address(),
                phone=generate_phone(),
                email=generate_email(f"customer{i}"),
                is_active=random.choice([True, True, True, False])  # %75 aktif
            )
            db.session.add(customer)
        db.session.commit()
        
        # 2. Yeni tedarikçiler ekle (10 tedarikçi daha)
        print("Yeni tedarikçiler ekleniyor...")
        for i in range(10):
            supplier = Supplier(
                name=random.choice(COMPANY_NAMES),
                tax_no=generate_tax_no(),
                address=generate_address(),
                phone=generate_phone(),
                email=generate_email(f"supplier{i}"),
                is_active=random.choice([True, True, True, False])  # %75 aktif
            )
            db.session.add(supplier)
        db.session.commit()
        
        # 3. Yeni ürünler ekle (50 ürün daha)
        print("Yeni ürünler ekleniyor...")
        for i in range(50):
            product = Product(
                sku=generate_sku(),
                name=f"Ürün {i+1} - {random.choice(PRODUCT_CATEGORIES)}",
                category=random.choice(PRODUCT_CATEGORIES),
                unit=random.choice(UNITS),
                barcode=generate_barcode(),
                reorder_point=random.randint(10, 100),
                safety_stock=random.randint(5, 50),
                is_active=random.choice([True, True, True, False])  # %75 aktif
            )
            db.session.add(product)
        db.session.commit()
        
        # Tüm verileri yeniden al
        all_customers = Customer.query.all()
        all_suppliers = Supplier.query.all()
        all_products = Product.query.all()
        all_warehouses = Warehouse.query.all()
        all_users = User.query.all()
        
        print(f"Güncellenmiş veriler: {len(all_customers)} müşteri, {len(all_suppliers)} tedarikçi, {len(all_products)} ürün")
        
        # 4. 3 aylık satış siparişleri oluştur (günde 2-5 sipariş)
        print("Satış siparişleri oluşturuluyor...")
        start_date = datetime.now() - timedelta(days=90)
        
        for day in range(90):
            current_date = start_date + timedelta(days=day)
            orders_per_day = random.randint(2, 5)
            
            for order_num in range(orders_per_day):
                # Sipariş oluştur
                sales_order = SalesOrder(
                    customer_id=random.choice(all_customers).id,
                    order_no=f"SO{current_date.strftime('%Y%m%d')}{order_num+1:03d}",
                    status=random.choice(list(SalesOrderStatus)),
                    order_date=current_date.date(),
                    expected_ship_date=(current_date + timedelta(days=random.randint(1, 7))).date(),
                    note=f"Sipariş notu - {current_date.strftime('%d.%m.%Y')}"
                )
                db.session.add(sales_order)
                db.session.flush()  # ID'yi almak için
                
                # Sipariş satırları oluştur (1-5 satır)
                lines_count = random.randint(1, 5)
                for line_num in range(lines_count):
                    product = random.choice(all_products)
                    sales_line = SalesOrderLine(
                        sales_order_id=sales_order.id,
                        product_id=product.id,
                        qty=random.randint(1, 20),
                        unit_price=Decimal(str(round(random.uniform(10.0, 500.0), 2))),
                        shipped_qty=random.randint(0, 20) if sales_order.status in [SalesOrderStatus.PARTIALLY_SHIPPED, SalesOrderStatus.CLOSED] else 0,
                        status=random.choice(['Pending', 'Shipped', 'Closed'])
                    )
                    db.session.add(sales_line)
        
        db.session.commit()
        
        # 5. 3 aylık satın alma siparişleri oluştur (haftada 3-8 sipariş)
        print("Satın alma siparişleri oluşturuluyor...")
        
        for week in range(13):  # 13 hafta = 3 ay
            week_start = start_date + timedelta(weeks=week)
            orders_per_week = random.randint(3, 8)
            
            for order_num in range(orders_per_week):
                order_date = week_start + timedelta(days=random.randint(0, 6))
                
                # Sipariş oluştur
                purchase_order = PurchaseOrder(
                    supplier_id=random.choice(all_suppliers).id,
                    order_no=f"PO{order_date.strftime('%Y%m%d')}{order_num+1:03d}",
                    status=random.choice(list(PurchaseOrderStatus)),
                    order_date=order_date.date(),
                    expected_date=(order_date + timedelta(days=random.randint(7, 21))).date(),
                    note=f"Satın alma notu - {order_date.strftime('%d.%m.%Y')}"
                )
                db.session.add(purchase_order)
                db.session.flush()  # ID'yi almak için
                
                # Sipariş satırları oluştur (2-8 satır)
                lines_count = random.randint(2, 8)
                for line_num in range(lines_count):
                    product = random.choice(all_products)
                    purchase_line = PurchaseOrderLine(
                        purchase_order_id=purchase_order.id,
                        product_id=product.id,
                        qty=random.randint(10, 100),
                        unit_price=Decimal(str(round(random.uniform(5.0, 200.0), 2))),
                        received_qty=random.randint(0, 100) if purchase_order.status in [PurchaseOrderStatus.PARTIALLY_RECEIVED, PurchaseOrderStatus.CLOSED] else 0,
                        status=random.choice(['Pending', 'Received', 'Closed'])
                    )
                    db.session.add(purchase_line)
        
        db.session.commit()
        
        # 6. Stok hareketleri oluştur (günde 5-15 hareket)
        print("Stok hareketleri oluşturuluyor...")
        
        for day in range(90):
            current_date = start_date + timedelta(days=day)
            movements_per_day = random.randint(5, 15)
            
            for movement_num in range(movements_per_day):
                product = random.choice(all_products)
                warehouse = random.choice(all_warehouses)
                
                # Hareket türüne göre yön belirle
                movement_type = random.choice(list(MovementType))
                if movement_type in [MovementType.PURCHASE, MovementType.ADJUSTMENT]:
                    direction = MovementDirection.IN
                elif movement_type == MovementType.SALES:
                    direction = MovementDirection.OUT
                else:  # TRANSFER
                    direction = random.choice(list(MovementDirection))
                
                stock_movement = StockMovement(
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    direction=direction,
                    quantity=random.randint(1, 50),
                    movement_type=movement_type,
                    ref_document_no=f"REF{current_date.strftime('%Y%m%d')}{movement_num+1:03d}",
                    ref_line_id=random.randint(1, 1000),
                    note=f"Hareket notu - {current_date.strftime('%d.%m.%Y')}",
                    created_by=random.choice(all_users).id
                )
                db.session.add(stock_movement)
        
        db.session.commit()
        
        # 7. Envanter bakiyelerini güncelle
        print("Envanter bakiyeleri güncelleniyor...")
        
        # Mevcut bakiyeleri sıfırla ve yeniden hesapla
        InventoryBalance.query.delete()
        
        for product in all_products:
            for warehouse in all_warehouses:
                # Bu ürün-depo kombinasyonu için stok hareketlerini hesapla
                movements = StockMovement.query.filter_by(
                    product_id=product.id,
                    warehouse_id=warehouse.id
                ).all()
                
                on_hand = 0
                for movement in movements:
                    if movement.direction == MovementDirection.IN:
                        on_hand += movement.quantity
                    else:
                        on_hand -= movement.quantity
                
                on_hand = max(0, on_hand)  # Negatif stok olmasın
                reserved = random.randint(0, min(10, on_hand))  # Rastgele rezerve miktar
                available = max(0, on_hand - reserved)
                
                balance = InventoryBalance(
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    on_hand_qty=on_hand,
                    reserved_qty=reserved,
                    available_qty=available
                )
                db.session.add(balance)
        
        db.session.commit()
        
        # 8. Yeniden sipariş kuralları oluştur
        print("Yeniden sipariş kuralları oluşturuluyor...")
        
        for product in all_products:
            # Her ürün için 1-3 tedarikçi ile kural oluştur
            suppliers_for_product = random.sample(all_suppliers, random.randint(1, min(3, len(all_suppliers))))
            
            for supplier in suppliers_for_product:
                rule = ReorderRule(
                    product_id=product.id,
                    supplier_id=supplier.id,
                    moq=random.randint(10, 100),  # Minimum sipariş miktarı
                    lead_time_days=random.randint(3, 21),  # Teslim süresi
                    is_active=random.choice([True, True, True, False])  # %75 aktif
                )
                db.session.add(rule)
        
        db.session.commit()
        
        # 9. Audit logları oluştur
        print("Audit logları oluşturuluyor...")
        
        entities = ['customers', 'products', 'suppliers', 'sales_orders', 'purchase_orders']
        actions = ['CREATE', 'UPDATE', 'DELETE']
        
        for day in range(90):
            current_date = start_date + timedelta(days=day)
            logs_per_day = random.randint(5, 20)
            
            for log_num in range(logs_per_day):
                audit_log = AuditLog(
                    entity=random.choice(entities),
                    entity_id=random.randint(1, 1000),
                    action=random.choice(actions),
                    diff_json=f'{{"field": "value_{log_num}", "old": "old_value", "new": "new_value"}}',
                    user_id=random.choice(all_users).id
                )
                db.session.add(audit_log)
        
        db.session.commit()
        
        # Sonuçları göster
        print("\n" + "="*50)
        print("SENTETİK VERİ ÜRETİMİ TAMAMLANDI!")
        print("="*50)
        
        print(f"Müşteriler: {Customer.query.count()}")
        print(f"Tedarikçiler: {Supplier.query.count()}")
        print(f"Ürünler: {Product.query.count()}")
        print(f"Depolar: {Warehouse.query.count()}")
        print(f"Kullanıcılar: {User.query.count()}")
        print(f"Satış Siparişleri: {SalesOrder.query.count()}")
        print(f"Satış Sipariş Satırları: {SalesOrderLine.query.count()}")
        print(f"Satın Alma Siparişleri: {PurchaseOrder.query.count()}")
        print(f"Satın Alma Sipariş Satırları: {PurchaseOrderLine.query.count()}")
        print(f"Stok Hareketleri: {StockMovement.query.count()}")
        print(f"Envanter Bakiyeleri: {InventoryBalance.query.count()}")
        print(f"Yeniden Sipariş Kuralları: {ReorderRule.query.count()}")
        print(f"Audit Logları: {AuditLog.query.count()}")

if __name__ == "__main__":
    generate_synthetic_data()
