#!/usr/bin/env python3
"""
ERP Data Export to Excel
This script exports all data from the mini ERP system to Excel files.
"""

import pandas as pd
from datetime import datetime
import os
from app import create_app, db
from app.models import (
    Customer, Product, Supplier, Warehouse, User, 
    SalesOrder, SalesOrderLine, PurchaseOrder, PurchaseOrderLine,
    StockMovement, InventoryBalance, ReorderRule, AuditLog
)

def export_all_data():
    """Export all ERP data to Excel files"""
    
    # Create Flask app context
    app = create_app()
    with app.app_context():
        
        # Create export directory
        export_dir = "excel_exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("Starting data export...")
        
        # Export each table to separate Excel sheets
        exports = {}
        
        # 1. Customers
        print("Exporting customers...")
        customers = Customer.query.all()
        customers_data = []
        for customer in customers:
            customer_dict = customer.to_dict()
            customers_data.append(customer_dict)
        
        if customers_data:
            customers_df = pd.DataFrame(customers_data)
            exports['customers'] = customers_df
        
        # 2. Suppliers
        print("Exporting suppliers...")
        suppliers = Supplier.query.all()
        suppliers_data = []
        for supplier in suppliers:
            supplier_dict = supplier.to_dict()
            suppliers_data.append(supplier_dict)
        
        if suppliers_data:
            suppliers_df = pd.DataFrame(suppliers_data)
            exports['suppliers'] = suppliers_df
        
        # 3. Products
        print("Exporting products...")
        products = Product.query.all()
        products_data = []
        for product in products:
            product_dict = product.to_dict()
            products_data.append(product_dict)
        
        if products_data:
            products_df = pd.DataFrame(products_data)
            exports['products'] = products_df
        
        # 4. Warehouses
        print("Exporting warehouses...")
        warehouses = Warehouse.query.all()
        warehouses_data = []
        for warehouse in warehouses:
            warehouse_dict = warehouse.to_dict()
            warehouses_data.append(warehouse_dict)
        
        if warehouses_data:
            warehouses_df = pd.DataFrame(warehouses_data)
            exports['warehouses'] = warehouses_df
        
        # 5. Users
        print("Exporting users...")
        users = User.query.all()
        users_data = []
        for user in users:
            user_dict = user.to_dict()  # This excludes password_hash
            users_data.append(user_dict)
        
        if users_data:
            users_df = pd.DataFrame(users_data)
            exports['users'] = users_df
        
        # 6. Sales Orders
        print("Exporting sales orders...")
        sales_orders = SalesOrder.query.all()
        sales_orders_data = []
        for order in sales_orders:
            order_dict = order.to_dict()
            # Add customer name for better readability
            order_dict['customer_name'] = order.customer.name if order.customer else None
            sales_orders_data.append(order_dict)
        
        if sales_orders_data:
            sales_orders_df = pd.DataFrame(sales_orders_data)
            exports['sales_orders'] = sales_orders_df
        
        # 7. Sales Order Lines
        print("Exporting sales order lines...")
        sales_order_lines = SalesOrderLine.query.all()
        sales_order_lines_data = []
        for line in sales_order_lines:
            line_dict = line.to_dict()
            # Add product and order info for better readability
            line_dict['product_name'] = line.product.name if line.product else None
            line_dict['product_sku'] = line.product.sku if line.product else None
            line_dict['order_no'] = line.sales_order.order_no if line.sales_order else None
            line_dict['customer_name'] = line.sales_order.customer.name if line.sales_order and line.sales_order.customer else None
            sales_order_lines_data.append(line_dict)
        
        if sales_order_lines_data:
            sales_order_lines_df = pd.DataFrame(sales_order_lines_data)
            exports['sales_order_lines'] = sales_order_lines_df
        
        # 8. Purchase Orders
        print("Exporting purchase orders...")
        purchase_orders = PurchaseOrder.query.all()
        purchase_orders_data = []
        for order in purchase_orders:
            order_dict = order.to_dict()
            # Add supplier name for better readability
            order_dict['supplier_name'] = order.supplier.name if order.supplier else None
            purchase_orders_data.append(order_dict)
        
        if purchase_orders_data:
            purchase_orders_df = pd.DataFrame(purchase_orders_data)
            exports['purchase_orders'] = purchase_orders_df
        
        # 9. Purchase Order Lines
        print("Exporting purchase order lines...")
        purchase_order_lines = PurchaseOrderLine.query.all()
        purchase_order_lines_data = []
        for line in purchase_order_lines:
            line_dict = line.to_dict()
            # Add product and order info for better readability
            line_dict['product_name'] = line.product.name if line.product else None
            line_dict['product_sku'] = line.product.sku if line.product else None
            line_dict['order_no'] = line.purchase_order.order_no if line.purchase_order else None
            line_dict['supplier_name'] = line.purchase_order.supplier.name if line.purchase_order and line.purchase_order.supplier else None
            purchase_order_lines_data.append(line_dict)
        
        if purchase_order_lines_data:
            purchase_order_lines_df = pd.DataFrame(purchase_order_lines_data)
            exports['purchase_order_lines'] = purchase_order_lines_df
        
        # 10. Stock Movements
        print("Exporting stock movements...")
        stock_movements = StockMovement.query.all()
        stock_movements_data = []
        for movement in stock_movements:
            movement_dict = movement.to_dict()
            # Add product and warehouse info for better readability
            movement_dict['product_name'] = movement.product.name if movement.product else None
            movement_dict['product_sku'] = movement.product.sku if movement.product else None
            movement_dict['warehouse_name'] = movement.warehouse.name if movement.warehouse else None
            movement_dict['created_by_username'] = movement.user.username if movement.user else None
            stock_movements_data.append(movement_dict)
        
        if stock_movements_data:
            stock_movements_df = pd.DataFrame(stock_movements_data)
            exports['stock_movements'] = stock_movements_df
        
        # 11. Inventory Balances
        print("Exporting inventory balances...")
        inventory_balances = InventoryBalance.query.all()
        inventory_balances_data = []
        for balance in inventory_balances:
            balance_dict = balance.to_dict()
            # Add product and warehouse info for better readability
            balance_dict['product_name'] = balance.product.name if balance.product else None
            balance_dict['product_sku'] = balance.product.sku if balance.product else None
            balance_dict['warehouse_name'] = balance.warehouse.name if balance.warehouse else None
            inventory_balances_data.append(balance_dict)
        
        if inventory_balances_data:
            inventory_balances_df = pd.DataFrame(inventory_balances_data)
            exports['inventory_balances'] = inventory_balances_df
        
        # 12. Reorder Rules
        print("Exporting reorder rules...")
        reorder_rules = ReorderRule.query.all()
        reorder_rules_data = []
        for rule in reorder_rules:
            rule_dict = rule.to_dict()
            # Add product and supplier info for better readability
            rule_dict['product_name'] = rule.product.name if rule.product else None
            rule_dict['product_sku'] = rule.product.sku if rule.product else None
            rule_dict['supplier_name'] = rule.supplier.name if rule.supplier else None
            reorder_rules_data.append(rule_dict)
        
        if reorder_rules_data:
            reorder_rules_df = pd.DataFrame(reorder_rules_data)
            exports['reorder_rules'] = reorder_rules_df
        
        # 13. Audit Logs
        print("Exporting audit logs...")
        audit_logs = AuditLog.query.all()
        audit_logs_data = []
        for log in audit_logs:
            log_dict = log.to_dict()
            # Add user info for better readability
            log_dict['user_username'] = log.user.username if log.user else None
            audit_logs_data.append(log_dict)
        
        if audit_logs_data:
            audit_logs_df = pd.DataFrame(audit_logs_data)
            exports['audit_logs'] = audit_logs_df
        
        # Create comprehensive Excel file with all data
        excel_filename = f"{export_dir}/erp_data_export_{timestamp}.xlsx"
        print(f"Creating comprehensive Excel file: {excel_filename}")
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            for sheet_name, df in exports.items():
                if not df.empty:
                    # Clean column names for better Excel display
                    df.columns = [col.replace('_', ' ').title() for col in df.columns]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"  - Added sheet '{sheet_name}' with {len(df)} rows")
        
        # Also create individual Excel files for each table
        print("\nCreating individual Excel files...")
        for sheet_name, df in exports.items():
            if not df.empty:
                individual_filename = f"{export_dir}/{sheet_name}_{timestamp}.xlsx"
                # Clean column names for better Excel display
                df.columns = [col.replace('_', ' ').title() for col in df.columns]
                df.to_excel(individual_filename, index=False)
                print(f"  - Created {individual_filename} with {len(df)} rows")
        
        print(f"\nExport completed successfully!")
        print(f"All data exported to: {export_dir}/")
        print(f"Comprehensive file: {excel_filename}")
        
        # Print summary
        print("\nExport Summary:")
        print("=" * 50)
        for sheet_name, df in exports.items():
            if not df.empty:
                print(f"{sheet_name.replace('_', ' ').title()}: {len(df)} records")
            else:
                print(f"{sheet_name.replace('_', ' ').title()}: No data")

if __name__ == "__main__":
    export_all_data()



