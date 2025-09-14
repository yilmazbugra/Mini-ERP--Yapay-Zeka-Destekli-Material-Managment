#!/usr/bin/env python3
"""
AI/ML sistemini güçlendirmek için gelişmiş test verileri oluşturur
"""

import random
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
import numpy as np

# Faker'ı Türkçe için ayarla
fake = Faker('tr_TR')

def create_enhanced_seed_data():
    """AI/ML için gelişmiş test verileri oluştur"""
    
    from app import create_app, db
    from app.models import (
        Product, Warehouse, Customer, Supplier, SalesOrder, SalesOrderLine,
        PurchaseOrder, PurchaseOrderLine, StockMovement, InventoryBalance
    )
    
    app = create_app()
    
    with app.app_context():
        print("🚀 AI/ML için gelişmiş test verileri oluşturuluyor...")
        
        # Mevcut verileri temizle
        print("🧹 Mevcut veriler temizleniyor...")
        db.session.query(StockMovement).delete()
        db.session.query(SalesOrderLine).delete()
        db.session.query(SalesOrder).delete()
        db.session.query(PurchaseOrderLine).delete()
        db.session.query(PurchaseOrder).delete()
        db.session.query(InventoryBalance).delete()
        db.session.query(Customer).delete()
        db.session.query(Supplier).delete()
        db.session.query(Product).delete()
        db.session.query(Warehouse).delete()
        db.session.commit()
        
        # 1. Depolar oluştur
        print("🏢 Depolar oluşturuluyor...")
        warehouses = []
        warehouse_names = [
            "Merkez Depo", "İstanbul Depo", "Ankara Depo", 
            "İzmir Depo", "Bursa Depo", "Antalya Depo"
        ]
        
        for i, name in enumerate(warehouse_names):
            warehouse = Warehouse(
                name=name,
                code=f"WH{i+1:03d}",
                address=fake.address(),
                is_active=True
            )
            warehouses.append(warehouse)
            db.session.add(warehouse)
        
        db.session.commit()
        
        # 2. Kategoriler ve ürünler oluştur
        print("📦 Ürünler oluşturuluyor...")
        categories = [
            "Elektronik", "Giyim", "Ev & Yaşam", "Spor", "Kitap", 
            "Kozmetik", "Gıda", "Oyuncak", "Bahçe", "Otomotiv"
        ]
        
        products = []
        product_names = {
            "Elektronik": ["Laptop", "Telefon", "Tablet", "Kulaklık", "Kamera", "Televizyon", "Bilgisayar", "Mouse", "Klavye"],
            "Giyim": ["Tişört", "Pantolon", "Elbise", "Ayakkabı", "Ceket", "Gömlek", "Etek", "Sweatshirt"],
            "Ev & Yaşam": ["Masa", "Sandalye", "Yatak", "Dolap", "Lamba", "Halı", "Perde", "Vazo"],
            "Spor": ["Koşu Ayakkabısı", "Spor Tişörtü", "Spor Pantolonu", "Dambıl", "Yoga Matı", "Bisiklet", "Futbol Topu"],
            "Kitap": ["Roman", "Bilim Kurgu", "Tarih", "Felsefe", "Çocuk Kitabı", "Dergi", "Ansiklopedi"],
            "Kozmetik": ["Ruj", "Fondöten", "Krem", "Şampuan", "Parfüm", "Makyaj Seti", "Cilt Bakımı"],
            "Gıda": ["Çikolata", "Bisküvi", "Kahve", "Çay", "Meyve Suyu", "Konserve", "Dondurulmuş Gıda"],
            "Oyuncak": ["Oyuncak Araba", "Bebek", "Puzzle", "Lego", "Top", "Oyuncak Hayvan", "Eğitici Oyuncak"],
            "Bahçe": ["Çiçek Tohumu", "Saksı", "Bahçe Aleti", "Gübre", "Fidan", "Bahçe Mobilyası"],
            "Otomotiv": ["Lastik", "Motor Yağı", "Fren Balata", "Akü", "Filtre", "Ayna", "Koltuk Kılıfı"]
        }
        
        for category in categories:
            for i in range(15):  # Her kategoriden 15 ürün
                product_name = random.choice(product_names[category])
                sku = f"{category[:3].upper()}-{i+1:03d}"
                
                # Sezonsal ürünler için farklı reorder point'ler
                if category in ["Giyim", "Spor"]:
                    reorder_point = random.randint(20, 50)
                    safety_stock = random.randint(30, 80)
                elif category in ["Elektronik", "Ev & Yaşam"]:
                    reorder_point = random.randint(5, 15)
                    safety_stock = random.randint(10, 25)
                else:
                    reorder_point = random.randint(10, 30)
                    safety_stock = random.randint(15, 40)
                
                product = Product(
                    sku=sku,
                    name=f"{product_name} {fake.word().title()}",
                    category=category,
                    unit="adet",
                    barcode=fake.ean13(),
                    reorder_point=reorder_point,
                    safety_stock=safety_stock,
                    is_active=True
                )
                products.append(product)
                db.session.add(product)
        
        db.session.commit()
        
        # 3. Müşteriler oluştur
        print("👥 Müşteriler oluşturuluyor...")
        customers = []
        customer_segments = ["VIP", "Regular", "New", "At Risk", "Champions"]
        
        for i in range(100):
            customer = Customer(
                name=fake.company(),
                tax_no=fake.random_number(digits=10),
                address=fake.address(),
                phone=fake.phone_number(),
                email=fake.email(),
                is_active=True
            )
            customers.append(customer)
            db.session.add(customer)
        
        db.session.commit()
        
        # 4. Tedarikçiler oluştur
        print("🏭 Tedarikçiler oluşturuluyor...")
        suppliers = []
        
        for i in range(20):
            supplier = Supplier(
                name=fake.company(),
                tax_no=fake.random_number(digits=10),
                phone=fake.phone_number(),
                email=fake.email(),
                address=fake.address(),
                is_active=True
            )
            suppliers.append(supplier)
            db.session.add(supplier)
        
        db.session.commit()
        
        # 5. Envanter bakiyeleri oluştur
        print("📊 Envanter bakiyeleri oluşturuluyor...")
        
        for product in products:
            for warehouse in warehouses:
                # Rastgele stok miktarları
                on_hand = random.randint(0, 200)
                reserved = random.randint(0, min(20, on_hand))
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
        
        # 6. Geçmiş satış siparişleri oluştur (2 yıl)
        print("💰 Satış siparişleri oluşturuluyor...")
        
        start_date = datetime.now() - timedelta(days=730)  # 2 yıl önce
        
        for day in range(730):
            current_date = start_date + timedelta(days=day)
            
            # Hafta sonları daha az sipariş
            if current_date.weekday() >= 5:  # Cumartesi, Pazar
                order_count = random.randint(0, 3)
            else:
                order_count = random.randint(2, 8)
            
            # Sezonsal etkiler
            if current_date.month in [12, 1, 2]:  # Kış
                order_count = int(order_count * 1.3)
            elif current_date.month in [6, 7, 8]:  # Yaz
                order_count = int(order_count * 1.2)
            
            for _ in range(order_count):
                customer = random.choice(customers)
                order = SalesOrder(
                    customer_id=customer.id,
                    order_no=f"SO-{current_date.strftime('%Y%m%d')}-{random.randint(10000, 99999)}",
                    status=random.choice(['APPROVED', 'PARTIALLY_SHIPPED', 'CLOSED']),
                    order_date=current_date.date(),
                    expected_ship_date=(current_date + timedelta(days=random.randint(1, 7))).date(),
                    note=fake.sentence()
                )
                db.session.add(order)
                db.session.flush()  # ID'yi almak için
                
                # Sipariş kalemleri
                line_count = random.randint(1, 5)
                selected_products = random.sample(products, min(line_count, len(products)))
                
                for product in selected_products:
                    qty = random.randint(1, 10)
                    unit_price = random.uniform(10, 500)
                    
                    line = SalesOrderLine(
                        sales_order_id=order.id,
                        product_id=product.id,
                        qty=qty,
                        unit_price=unit_price,
                        shipped_qty=random.randint(0, qty),
                        status=random.choice(['Pending', 'Shipped', 'Closed'])
                    )
                    db.session.add(line)
        
        db.session.commit()
        
        # 7. Stok hareketleri oluştur
        print("📈 Stok hareketleri oluşturuluyor...")
        
        for day in range(730):
            current_date = start_date + timedelta(days=day)
            
            # Her gün rastgele stok hareketleri
            movement_count = random.randint(5, 20)
            
            for _ in range(movement_count):
                product = random.choice(products)
                warehouse = random.choice(warehouses)
                direction = random.choice(['IN', 'OUT'])
                
                if direction == 'IN':
                    quantity = random.randint(10, 100)
                    movement_type = random.choice(['PURCHASE', 'ADJUSTMENT'])
                else:
                    quantity = random.randint(1, 20)
                    movement_type = random.choice(['SALES', 'ADJUSTMENT'])
                
                movement = StockMovement(
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    direction=direction,
                    quantity=quantity,
                    movement_type=movement_type,
                    ref_document_no=f"REF-{random.randint(10000, 99999)}",
                    note=fake.sentence(),
                    created_at=current_date
                )
                db.session.add(movement)
        
        db.session.commit()
        
        # 8. Satın alma siparişleri oluştur
        print("🛒 Satın alma siparişleri oluşturuluyor...")
        
        for day in range(730):
            current_date = start_date + timedelta(days=day)
            
            # Ayda 2-3 satın alma siparişi
            if random.random() < 0.1:  # %10 ihtimal
                supplier = random.choice(suppliers)
                order = PurchaseOrder(
                    supplier_id=supplier.id,
                    order_no=f"PO-{current_date.strftime('%Y%m%d')}-{random.randint(10000, 99999)}",
                    status=random.choice(['DRAFT', 'APPROVED', 'PARTIALLY_RECEIVED']),
                    order_date=current_date.date(),
                    expected_date=(current_date + timedelta(days=random.randint(7, 21))).date(),
                    note=fake.sentence()
                )
                db.session.add(order)
                db.session.flush()
                
                # Sipariş kalemleri
                line_count = random.randint(1, 8)
                selected_products = random.sample(products, min(line_count, len(products)))
                
                for product in selected_products:
                    qty = random.randint(20, 200)
                    unit_price = random.uniform(5, 200)
                    
                    line = PurchaseOrderLine(
                        purchase_order_id=order.id,
                        product_id=product.id,
                        qty=qty,
                        unit_price=unit_price,
                        received_qty=random.randint(0, qty)
                    )
                    db.session.add(line)
        
        db.session.commit()
        
        # 9. Envanter bakiyelerini güncelle (stok hareketlerine göre)
        print("🔄 Envanter bakiyeleri güncelleniyor...")
        
        for product in products:
            for warehouse in warehouses:
                balance = db.session.query(InventoryBalance).filter(
                    InventoryBalance.product_id == product.id,
                    InventoryBalance.warehouse_id == warehouse.id
                ).first()
                
                if balance:
                    # Stok hareketlerini hesapla
                    movements = db.session.query(StockMovement).filter(
                        StockMovement.product_id == product.id,
                        StockMovement.warehouse_id == warehouse.id
                    ).all()
                    
                    on_hand = 0
                    for movement in movements:
                        if movement.direction == 'IN':
                            on_hand += movement.quantity
                        else:
                            on_hand -= movement.quantity
                    
                    balance.on_hand_qty = max(0, on_hand)
                    balance.reserved_qty = random.randint(0, min(10, balance.on_hand_qty))
                    balance.available_qty = max(0, balance.on_hand_qty - balance.reserved_qty)
        
        db.session.commit()
        
        print("✅ AI/ML için gelişmiş test verileri başarıyla oluşturuldu!")
        print(f"📊 Oluşturulan veriler:")
        print(f"   🏢 Depolar: {len(warehouses)}")
        print(f"   📦 Ürünler: {len(products)}")
        print(f"   👥 Müşteriler: {len(customers)}")
        print(f"   🏭 Tedarikçiler: {len(suppliers)}")
        print(f"   💰 Satış siparişleri: {db.session.query(SalesOrder).count()}")
        print(f"   📈 Stok hareketleri: {db.session.query(StockMovement).count()}")
        print(f"   🛒 Satın alma siparişleri: {db.session.query(PurchaseOrder).count()}")
        
        return True

if __name__ == "__main__":
    create_enhanced_seed_data()
