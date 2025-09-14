#!/usr/bin/env python3
"""
Veritabanındaki enum değerlerini SQL ile düzeltir
"""

import sqlite3
import os

def fix_database_enums():
    """SQLite veritabanındaki enum değerlerini düzelt"""
    
    db_path = 'instance/mini_erp.db'
    
    if not os.path.exists(db_path):
        print("❌ Veritabanı bulunamadı!")
        return
    
    print("🔧 Veritabanı enum değerleri düzeltiliyor...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # SalesOrder status değerlerini düzelt
        print("📝 Satış siparişleri düzeltiliyor...")
        cursor.execute("""
            UPDATE sales_orders 
            SET status = 'APPROVED' 
            WHERE status = 'Approved'
        """)
        
        cursor.execute("""
            UPDATE sales_orders 
            SET status = 'PARTIALLY_SHIPPED' 
            WHERE status = 'PartiallyShipped'
        """)
        
        cursor.execute("""
            UPDATE sales_orders 
            SET status = 'CLOSED' 
            WHERE status = 'Closed'
        """)
        
        # PurchaseOrder status değerlerini düzelt
        print("📝 Satın alma siparişleri düzeltiliyor...")
        cursor.execute("""
            UPDATE purchase_orders 
            SET status = 'DRAFT' 
            WHERE status = 'Draft'
        """)
        
        cursor.execute("""
            UPDATE purchase_orders 
            SET status = 'APPROVED' 
            WHERE status = 'Approved'
        """)
        
        cursor.execute("""
            UPDATE purchase_orders 
            SET status = 'PARTIALLY_RECEIVED' 
            WHERE status = 'PartiallyReceived'
        """)
        
        cursor.execute("""
            UPDATE purchase_orders 
            SET status = 'CLOSED' 
            WHERE status = 'Closed'
        """)
        
        # Değişiklikleri kaydet
        conn.commit()
        
        # İstatistikler
        cursor.execute("SELECT COUNT(*) FROM sales_orders")
        sales_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM purchase_orders")
        purchase_count = cursor.fetchone()[0]
        
        print("✅ Enum değerleri başarıyla düzeltildi!")
        print(f"📊 Toplam satış siparişi: {sales_count}")
        print(f"📊 Toplam satın alma siparişi: {purchase_count}")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_enums()
