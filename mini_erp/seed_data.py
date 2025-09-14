#!/usr/bin/env python3
"""
Seed data script for Mini ERP
Creates initial users, products, warehouses, and other essential data
"""

from app import create_app, db
from app.models import User, Product, Warehouse, Supplier, Customer, InventoryBalance
from werkzeug.security import generate_password_hash

def create_users():
    """Create initial users"""
    print("Creating users...")
    
    # Check if admin user already exists
    if User.query.filter_by(username='admin').first():
        print("Admin user already exists")
        return
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@minierp.com',
        role='admin',
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create warehouse manager
    warehouse_manager = User(
        username='warehouse_manager',
        email='warehouse@minierp.com',
        role='warehouse_manager',   
        is_active=True
    )
    warehouse_manager.set_password('warehouse123')
    db.session.add(warehouse_manager)
    
    # Create clerk
    clerk = User(
        username='clerk',
        email='clerk@minierp.com',
        role='clerk',
        is_active=True
    )
    clerk.set_password('clerk123')
    db.session.add(clerk)
    
    # Create viewer
    viewer = User(
        username='viewer',
        email='viewer@minierp.com',
        role='viewer',
        is_active=True
    )
    viewer.set_password('viewer123')
    db.session.add(viewer)
    
    print("Users created successfully")

def create_warehouses():
    """Create initial warehouses"""
    print("Creating warehouses...")
    
    warehouses_data = [
        {'name': 'Ana Depo', 'code': 'AD001', 'address': 'İstanbul, Türkiye'},
        {'name': 'Şube Depo', 'code': 'SD001', 'address': 'Ankara, Türkiye'},
        {'name': 'Satış Deposu', 'code': 'SD002', 'address': 'İzmir, Türkiye'},
        {'name': 'Yedek Depo', 'code': 'YD001', 'address': 'Bursa, Türkiye'}
    ]
    
    for warehouse_data in warehouses_data:
        if not Warehouse.query.filter_by(name=warehouse_data['name']).first():
            warehouse = Warehouse(**warehouse_data)
            db.session.add(warehouse)
    
    print("Warehouses created successfully")

def create_products():
    """Create initial products"""
    print("Creating products...")
    
    products_data = [
        {
            'sku': 'PROD-001',
            'name': 'Laptop Bilgisayar',
            'category': 'Elektronik',
            'unit': 'adet',
            'barcode': '1234567890123',
            'reorder_point': 5,
            'safety_stock': 10
        },
        {
            'sku': 'PROD-002',
            'name': 'Masaüstü Bilgisayar',
            'category': 'Elektronik',
            'unit': 'adet',
            'barcode': '1234567890124',
            'reorder_point': 3,
            'safety_stock': 8
        },
        {
            'sku': 'PROD-003',
            'name': 'Monitör',
            'category': 'Elektronik',
            'unit': 'adet',
            'barcode': '1234567890125',
            'reorder_point': 10,
            'safety_stock': 20
        },
        {
            'sku': 'PROD-004',
            'name': 'Klavye',
            'category': 'Aksesuar',
            'unit': 'adet',
            'barcode': '1234567890126',
            'reorder_point': 20,
            'safety_stock': 50
        },
        {
            'sku': 'PROD-005',
            'name': 'Mouse',
            'category': 'Aksesuar',
            'unit': 'adet',
            'barcode': '1234567890127',
            'reorder_point': 30,
            'safety_stock': 60
        },
        {
            'sku': 'PROD-006',
            'name': 'Yazıcı',
            'category': 'Ofis',
            'unit': 'adet',
            'barcode': '1234567890128',
            'reorder_point': 2,
            'safety_stock': 5
        },
        {
            'sku': 'PROD-007',
            'name': 'Telefon',
            'category': 'Elektronik',
            'unit': 'adet',
            'barcode': '1234567890129',
            'reorder_point': 8,
            'safety_stock': 15
        }
    ]
    
    for product_data in products_data:
        if not Product.query.filter_by(sku=product_data['sku']).first():
            product = Product(**product_data)
            db.session.add(product)
    
    print("Products created successfully")

def create_suppliers():
    """Create initial suppliers"""
    print("Creating suppliers...")
    
    suppliers_data = [
        {
            'name': 'ABC Teknoloji',
            'email': 'ahmet@abcteknoloji.com',
            'phone': '+90 212 555 0101',
            'address': 'İstanbul, Türkiye',
            'tax_no': '1234567890'
        },
        {
            'name': 'XYZ Elektronik',
            'email': 'mehmet@xyzelektronik.com',
            'phone': '+90 312 555 0202',
            'address': 'Ankara, Türkiye',
            'tax_no': '0987654321'
        },
        {
            'name': 'DEF Bilgisayar',
            'email': 'ayse@defbilgisayar.com',
            'phone': '+90 232 555 0303',
            'address': 'İzmir, Türkiye',
            'tax_no': '1122334455'
        }
    ]
    
    for supplier_data in suppliers_data:
        if not Supplier.query.filter_by(name=supplier_data['name']).first():
            supplier = Supplier(**supplier_data)
            db.session.add(supplier)
    
    print("Suppliers created successfully")

def create_customers():
    """Create initial customers"""
    print("Creating customers...")
    
    customers_data = [
        {
            'name': 'ABC Şirketi',
            'email': 'ali@abc.com',
            'phone': '+90 212 555 1001',
            'address': 'İstanbul, Türkiye',
            'tax_no': '1111111111'
        },
        {
            'name': 'XYZ Ltd.',
            'email': 'fatma@xyz.com',
            'phone': '+90 312 555 2002',
            'address': 'Ankara, Türkiye',
            'tax_no': '2222222222'
        },
        {
            'name': 'DEF A.Ş.',
            'email': 'mustafa@def.com',
            'phone': '+90 232 555 3003',
            'address': 'İzmir, Türkiye',
            'tax_no': '3333333333'
        }
    ]
    
    for customer_data in customers_data:
        if not Customer.query.filter_by(name=customer_data['name']).first():
            customer = Customer(**customer_data)
            db.session.add(customer)
    
    print("Customers created successfully")

def create_inventory_balances():
    """Create initial inventory balances"""
    print("Creating inventory balances...")
    
    # Get all products and warehouses
    products = Product.query.all()
    warehouses = Warehouse.query.all()
    
    if not products or not warehouses:
        print("No products or warehouses found. Skipping inventory balances.")
        return
    
    # Create inventory balances for each product in each warehouse
    for product in products:
        for warehouse in warehouses:
            if not InventoryBalance.query.filter_by(
                product_id=product.id, 
                warehouse_id=warehouse.id
            ).first():
                # Random initial stock
                import random
                on_hand_qty = random.randint(0, 50)
                
                balance = InventoryBalance(
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    on_hand_qty=on_hand_qty,
                    reserved_qty=0
                )
                balance.update_available_qty()
                db.session.add(balance)
    
    print("Inventory balances created successfully")

def main():
    """Main seed data function"""
    app = create_app()
    
    with app.app_context():
        print("Starting seed data creation...")
        
        # Create all tables
        db.create_all()
        
        # Create data
        create_users()
        create_warehouses()
        create_products()
        create_suppliers()
        create_customers()
        create_inventory_balances()
        
        # Commit all changes
        db.session.commit()
        
        print("Seed data creation completed successfully!")
        print("\nTest users created:")
        print("- admin / admin123 (Admin)")
        print("- warehouse_manager / warehouse123 (Warehouse Manager)")
        print("- clerk / clerk123 (Clerk)")
        print("- viewer / viewer123 (Viewer)")

if __name__ == '__main__':
    main()