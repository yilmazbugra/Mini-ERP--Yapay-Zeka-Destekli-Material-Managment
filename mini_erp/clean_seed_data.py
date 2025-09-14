from app import create_app, db
from app.models import *
from app.models.sales_order import SalesOrderStatus
from datetime import datetime, date, timedelta
import random

def create_clean_data():
    app = create_app()
    with app.app_context():
        print("🌱 Düzenli test verileri oluşturuluyor...")
        
        # 1. Ürünler - Sadece 3 kategori, düzenli
        print("📦 Ürünler oluşturuluyor...")
        products_data = [
            # Elektronik (20 ürün)
            {"sku": "ELE-001", "name": "Laptop Dell", "category": "Elektronik", "unit": "adet", "reorder_point": 5, "safety_stock": 10},
            {"sku": "ELE-002", "name": "Mouse Logitech", "category": "Elektronik", "unit": "adet", "reorder_point": 20, "safety_stock": 40},
            {"sku": "ELE-003", "name": "Klavye Mekanik", "category": "Elektronik", "unit": "adet", "reorder_point": 15, "safety_stock": 30},
            {"sku": "ELE-004", "name": "Monitör 24\"", "category": "Elektronik", "unit": "adet", "reorder_point": 8, "safety_stock": 16},
            {"sku": "ELE-005", "name": "Kulaklık Bluetooth", "category": "Elektronik", "unit": "adet", "reorder_point": 25, "safety_stock": 50},
            {"sku": "ELE-006", "name": "Webcam HD", "category": "Elektronik", "unit": "adet", "reorder_point": 10, "safety_stock": 20},
            {"sku": "ELE-007", "name": "Tablet 10\"", "category": "Elektronik", "unit": "adet", "reorder_point": 6, "safety_stock": 12},
            {"sku": "ELE-008", "name": "Telefon Samsung", "category": "Elektronik", "unit": "adet", "reorder_point": 12, "safety_stock": 24},
            {"sku": "ELE-009", "name": "Powerbank 10000mAh", "category": "Elektronik", "unit": "adet", "reorder_point": 30, "safety_stock": 60},
            {"sku": "ELE-010", "name": "USB Kablo", "category": "Elektronik", "unit": "adet", "reorder_point": 50, "safety_stock": 100},
            {"sku": "ELE-011", "name": "Hoparlör Bluetooth", "category": "Elektronik", "unit": "adet", "reorder_point": 15, "safety_stock": 30},
            {"sku": "ELE-012", "name": "Router WiFi", "category": "Elektronik", "unit": "adet", "reorder_point": 8, "safety_stock": 16},
            {"sku": "ELE-013", "name": "Hard Disk 1TB", "category": "Elektronik", "unit": "adet", "reorder_point": 10, "safety_stock": 20},
            {"sku": "ELE-014", "name": "SSD 256GB", "category": "Elektronik", "unit": "adet", "reorder_point": 15, "safety_stock": 30},
            {"sku": "ELE-015", "name": "RAM 8GB", "category": "Elektronik", "unit": "adet", "reorder_point": 20, "safety_stock": 40},
            {"sku": "ELE-016", "name": "İşlemci Intel i5", "category": "Elektronik", "unit": "adet", "reorder_point": 5, "safety_stock": 10},
            {"sku": "ELE-017", "name": "Anakart ASUS", "category": "Elektronik", "unit": "adet", "reorder_point": 6, "safety_stock": 12},
            {"sku": "ELE-018", "name": "Ekran Kartı RTX", "category": "Elektronik", "unit": "adet", "reorder_point": 4, "safety_stock": 8},
            {"sku": "ELE-019", "name": "Güç Kaynağı 600W", "category": "Elektronik", "unit": "adet", "reorder_point": 8, "safety_stock": 16},
            {"sku": "ELE-020", "name": "Kasa ATX", "category": "Elektronik", "unit": "adet", "reorder_point": 10, "safety_stock": 20},
            
            # Giyim (15 ürün)
            {"sku": "GİY-001", "name": "T-Shirt Erkek", "category": "Giyim", "unit": "adet", "reorder_point": 50, "safety_stock": 100},
            {"sku": "GİY-002", "name": "Jean Pantolon", "category": "Giyim", "unit": "adet", "reorder_point": 30, "safety_stock": 60},
            {"sku": "GİY-003", "name": "Sweatshirt", "category": "Giyim", "unit": "adet", "reorder_point": 25, "safety_stock": 50},
            {"sku": "GİY-004", "name": "Kazak Yün", "category": "Giyim", "unit": "adet", "reorder_point": 20, "safety_stock": 40},
            {"sku": "GİY-005", "name": "Ceket Deri", "category": "Giyim", "unit": "adet", "reorder_point": 15, "safety_stock": 30},
            {"sku": "GİY-006", "name": "Gömlek Beyaz", "category": "Giyim", "unit": "adet", "reorder_point": 40, "safety_stock": 80},
            {"sku": "GİY-007", "name": "Etek Siyah", "category": "Giyim", "unit": "adet", "reorder_point": 25, "safety_stock": 50},
            {"sku": "GİY-008", "name": "Elbise Yaz", "category": "Giyim", "unit": "adet", "reorder_point": 20, "safety_stock": 40},
            {"sku": "GİY-009", "name": "Mont Kış", "category": "Giyim", "unit": "adet", "reorder_point": 12, "safety_stock": 24},
            {"sku": "GİY-010", "name": "Ayakkabı Spor", "category": "Giyim", "unit": "adet", "reorder_point": 30, "safety_stock": 60},
            {"sku": "GİY-011", "name": "Bot Deri", "category": "Giyim", "unit": "adet", "reorder_point": 18, "safety_stock": 36},
            {"sku": "GİY-012", "name": "Çanta Sırt", "category": "Giyim", "unit": "adet", "reorder_point": 20, "safety_stock": 40},
            {"sku": "GİY-013", "name": "Kemer Deri", "category": "Giyim", "unit": "adet", "reorder_point": 35, "safety_stock": 70},
            {"sku": "GİY-014", "name": "Şapka Beyzbol", "category": "Giyim", "unit": "adet", "reorder_point": 40, "safety_stock": 80},
            {"sku": "GİY-015", "name": "Eldiven Deri", "category": "Giyim", "unit": "adet", "reorder_point": 25, "safety_stock": 50},
            
            # Ev & Yaşam (15 ürün)
            {"sku": "EV-001", "name": "Yatak Çarşafı", "category": "Ev & Yaşam", "unit": "takım", "reorder_point": 20, "safety_stock": 40},
            {"sku": "EV-002", "name": "Yastık Kılıfı", "category": "Ev & Yaşam", "unit": "adet", "reorder_point": 30, "safety_stock": 60},
            {"sku": "EV-003", "name": "Havlu Banyo", "category": "Ev & Yaşam", "unit": "adet", "reorder_point": 25, "safety_stock": 50},
            {"sku": "EV-004", "name": "Saksı Çiçek", "category": "Ev & Yaşam", "unit": "adet", "reorder_point": 15, "safety_stock": 30},
            {"sku": "EV-005", "name": "Masa Örtüsü", "category": "Ev & Yaşam", "unit": "adet", "reorder_point": 10, "safety_stock": 20},
            {"sku": "EV-006", "name": "Perde Salon", "category": "Ev & Yaşam", "unit": "takım", "reorder_point": 8, "safety_stock": 16},
            {"sku": "EV-007", "name": "Halı Yatak Odası", "category": "Ev & Yaşam", "unit": "adet", "reorder_point": 5, "safety_stock": 10},
            {"sku": "EV-008", "name": "Lamba Masa", "category": "Ev & Yaşam", "unit": "adet", "reorder_point": 12, "safety_stock": 24},
            {"sku": "EV-009", "name": "Vazo Seramik", "category": "Ev & Yaşam", "unit": "adet", "reorder_point": 15, "safety_stock": 30},
            {"sku": "EV-010", "name": "Tabak Porselen", "category": "Ev & Yaşam", "unit": "takım", "reorder_point": 20, "safety_stock": 40},
            {"sku": "EV-011", "name": "Bardak Cam", "category": "Ev & Yaşam", "unit": "takım", "reorder_point": 25, "safety_stock": 50},
            {"sku": "EV-012", "name": "Çatal Bıçak", "category": "Ev & Yaşam", "unit": "takım", "reorder_point": 30, "safety_stock": 60},
            {"sku": "EV-013", "name": "Tencere Seti", "category": "Ev & Yaşam", "unit": "takım", "reorder_point": 8, "safety_stock": 16},
            {"sku": "EV-014", "name": "Tava Döküm", "category": "Ev & Yaşam", "unit": "adet", "reorder_point": 10, "safety_stock": 20},
            {"sku": "EV-015", "name": "Mikser El", "category": "Ev & Yaşam", "unit": "adet", "reorder_point": 5, "safety_stock": 10},
        ]
        
        products = []
        for p_data in products_data:
            product = Product(
                sku=p_data["sku"],
                name=p_data["name"],
                category=p_data["category"],
                unit=p_data["unit"],
                reorder_point=p_data["reorder_point"],
                safety_stock=p_data["safety_stock"],
                barcode=f"{random.randint(1000000000000, 9999999999999)}",
                is_active=True
            )
            products.append(product)
            db.session.add(product)
        
        db.session.commit()
        print(f"✅ {len(products)} ürün oluşturuldu")
        
        # 2. Müşteriler - Düzenli
        print("👥 Müşteriler oluşturuluyor...")
        customers_data = [
            {"name": "ABC Teknoloji A.Ş.", "email": "info@abcteknoloji.com", "phone": "0212-555-0101"},
            {"name": "XYZ Giyim Ltd.", "email": "info@xyzgiyim.com", "phone": "0216-555-0102"},
            {"name": "Ev Yaşam Mağazası", "email": "info@evyasam.com", "phone": "0312-555-0103"},
            {"name": "Bilgisayar Dünyası", "email": "info@bilgisayardunyasi.com", "phone": "0212-555-0104"},
            {"name": "Moda Evi", "email": "info@modaevi.com", "phone": "0216-555-0105"},
            {"name": "Ev Dekorasyon", "email": "info@evdekorasyon.com", "phone": "0312-555-0106"},
            {"name": "Teknoloji Merkezi", "email": "info@teknolojimerkezi.com", "phone": "0212-555-0107"},
            {"name": "Giyim Mağazası", "email": "info@giyimmagazasi.com", "phone": "0216-555-0108"},
            {"name": "Ev & Bahçe", "email": "info@evbahce.com", "phone": "0312-555-0109"},
            {"name": "Elektronik Plus", "email": "info@elektronikplus.com", "phone": "0212-555-0110"},
        ]
        
        customers = []
        for c_data in customers_data:
            customer = Customer(
                name=c_data["name"],
                email=c_data["email"],
                phone=c_data["phone"],
                address=f"{random.randint(1, 999)}. Sokak No:{random.randint(1, 99)}",
                is_active=True
            )
            customers.append(customer)
            db.session.add(customer)
        
        db.session.commit()
        print(f"✅ {len(customers)} müşteri oluşturuldu")
        
        # 3. Tedarikçiler - Düzenli
        print("🏭 Tedarikçiler oluşturuluyor...")
        suppliers_data = [
            {"name": "Elektronik Tedarik A.Ş.", "email": "info@elektroniktedarik.com", "phone": "0212-555-0201"},
            {"name": "Giyim Üretim Ltd.", "email": "info@giyimuretim.com", "phone": "0216-555-0202"},
            {"name": "Ev Eşyası Fabrikası", "email": "info@evesyasi.com", "phone": "0312-555-0203"},
            {"name": "Teknoloji Distribütör", "email": "info@teknolojidistributor.com", "phone": "0212-555-0204"},
            {"name": "Moda Tasarım", "email": "info@modatasarim.com", "phone": "0216-555-0205"},
            {"name": "Ev Dekorasyon Üretim", "email": "info@evdekorasyonuretim.com", "phone": "0312-555-0206"},
        ]
        
        suppliers = []
        for s_data in suppliers_data:
            supplier = Supplier(
                name=s_data["name"],
                email=s_data["email"],
                phone=s_data["phone"],
                address=f"{random.randint(1, 999)}. Cadde No:{random.randint(1, 99)}",
                is_active=True
            )
            suppliers.append(supplier)
            db.session.add(supplier)
        
        db.session.commit()
        print(f"✅ {len(suppliers)} tedarikçi oluşturuldu")
        
        # 4. Depolar oluştur
        print("🏢 Depolar oluşturuluyor...")
        warehouses_data = [
            {'name': 'Merkez Depo', 'code': 'WH001', 'address': 'İstanbul Merkez'},
            {'name': 'İstanbul Depo', 'code': 'WH002', 'address': 'İstanbul Anadolu'},
            {'name': 'Ankara Depo', 'code': 'WH003', 'address': 'Ankara Merkez'},
            {'name': 'İzmir Depo', 'code': 'WH004', 'address': 'İzmir Merkez'},
            {'name': 'Bursa Depo', 'code': 'WH005', 'address': 'Bursa Merkez'},
            {'name': 'Antalya Depo', 'code': 'WH006', 'address': 'Antalya Merkez'},
        ]
        
        warehouses = []
        for w_data in warehouses_data:
            warehouse = Warehouse(
                name=w_data['name'],
                code=w_data['code'],
                address=w_data['address'],
                is_active=True
            )
            warehouses.append(warehouse)
            db.session.add(warehouse)
        
        db.session.commit()
        print(f"✅ {len(warehouses)} depo oluşturuldu")
        
        # 5. Stok bakiyeleri oluştur
        print("📈 Stok bakiyeleri oluşturuluyor...")
        
        for product in products:
            for warehouse in warehouses:
                # Rastgele stok miktarı (0-100 arası)
                on_hand = random.randint(0, 100)
                reserved = random.randint(0, min(10, on_hand))
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
        print("✅ Stok bakiyeleri oluşturuldu")
        
        # 5. Satış siparişleri oluştur (son 6 ay)
        print("🛒 Satış siparişleri oluşturuluyor...")
        sales_orders = []
        
        for i in range(200):  # 200 satış siparişi
            customer = random.choice(customers)
            order_date = date.today() - timedelta(days=random.randint(1, 180))
            
            sales_order = SalesOrder(
                customer_id=customer.id,
                order_no=f"SO-{order_date.strftime('%Y%m%d')}-{i+1:05d}",
                status=random.choice([SalesOrderStatus.APPROVED, SalesOrderStatus.CLOSED, SalesOrderStatus.PARTIALLY_SHIPPED]),
                order_date=order_date,
                expected_ship_date=order_date + timedelta(days=random.randint(1, 7)),
                note=f"Sipariş notu {i+1}"
            )
            db.session.add(sales_order)
            sales_orders.append(sales_order)
        
        db.session.commit()
        
        # Satış sipariş satırları
        for sales_order in sales_orders:
            # Her siparişe 1-5 arası ürün ekle
            num_products = random.randint(1, 5)
            selected_products = random.sample(products, min(num_products, len(products)))
            
            for product in selected_products:
                qty = random.randint(1, 10)
                unit_price = random.randint(50, 500)
                
                line = SalesOrderLine(
                    sales_order_id=sales_order.id,
                    product_id=product.id,
                    qty=qty,
                    unit_price=unit_price,
                    shipped_qty=random.randint(0, qty),
                    status=random.choice(['Pending', 'Shipped', 'Closed'])
                )
                db.session.add(line)
        
        db.session.commit()
        print("✅ Satış siparişleri oluşturuldu")
        
        # 6. Stok hareketleri oluştur
        print("📊 Stok hareketleri oluşturuluyor...")
        movement_types = ['PURCHASE', 'SALES', 'ADJUSTMENT', 'TRANSFER']
        
        for i in range(500):  # 500 stok hareketi
            product = random.choice(products)
            warehouse = random.choice(warehouses)
            movement_type = random.choice(movement_types)
            
            # Hareket miktarı
            if movement_type == 'SALES':
                quantity = -random.randint(1, 10)  # Satış negatif
            else:
                quantity = random.randint(1, 20)   # Diğerleri pozitif
            
            movement = StockMovement(
                product_id=product.id,
                warehouse_id=warehouse.id,
                movement_type=movement_type,
                quantity=quantity,
                ref_document_no=f"REF-{i+1:06d}",
                note=f"Hareket notu {i+1}",
                direction='IN' if quantity > 0 else 'OUT'
            )
            db.session.add(movement)
        
        db.session.commit()
        print("✅ Stok hareketleri oluşturuldu")
        
        print("\n🎉 Düzenli test verileri başarıyla oluşturuldu!")
        print(f"📦 Ürünler: {len(products)} adet (3 kategori)")
        print(f"👥 Müşteriler: {len(customers)} adet")
        print(f"🏭 Tedarikçiler: {len(suppliers)} adet")
        print(f"🛒 Satış Siparişleri: {len(sales_orders)} adet")
        print(f"📊 Stok Hareketleri: 500 adet")

if __name__ == "__main__":
    create_clean_data()
