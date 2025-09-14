from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import (
    Product, Warehouse, StockMovement, InventoryBalance,
    PurchaseOrder, SalesOrder, Supplier, Customer
)
from app.models.purchase_order import PurchaseOrderLine
from app.models.sales_order import SalesOrderLine
from app.models.stock_movement import MovementDirection, MovementType
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/low-stock', methods=['GET'])
@jwt_required()
def low_stock_report():
    """Get products with low stock (available <= reorder_point)"""
    warehouse_id = request.args.get('warehouse_id', type=int)
    
    query = db.session.query(
        Product.id, Product.sku, Product.name, Product.unit,
        Product.reorder_point, Product.safety_stock,
        Warehouse.id.label('warehouse_id'), Warehouse.name.label('warehouse_name'),
        InventoryBalance.available_qty
    ).select_from(InventoryBalance).join(Product).join(Warehouse).filter(
        InventoryBalance.available_qty <= Product.reorder_point
    )
    
    if warehouse_id:
        query = query.filter(InventoryBalance.warehouse_id == warehouse_id)
    
    results = query.all()
    
    low_stock_items = []
    for row in results:
        low_stock_items.append({
            'product_id': row.id,
            'sku': row.sku,
            'name': row.name,
            'unit': row.unit,
            'warehouse_id': row.warehouse_id,
            'warehouse_name': row.warehouse_name,
            'available_qty': row.available_qty,
            'reorder_point': row.reorder_point,
            'safety_stock': row.safety_stock,
            'shortage': row.reorder_point - row.available_qty
        })
    
    return jsonify({'low_stock_items': low_stock_items})

@reports_bp.route('/inventory-summary', methods=['GET'])
@jwt_required()
def inventory_summary():
    """Get inventory summary by warehouse"""
    warehouse_id = request.args.get('warehouse_id', type=int)
    
    query = db.session.query(
        Warehouse.id, Warehouse.name, Warehouse.code,
        func.count(InventoryBalance.id).label('product_count'),
        func.sum(InventoryBalance.on_hand_qty).label('total_on_hand'),
        func.sum(InventoryBalance.reserved_qty).label('total_reserved'),
        func.sum(InventoryBalance.available_qty).label('total_available')
    ).join(InventoryBalance).group_by(Warehouse.id, Warehouse.name, Warehouse.code)
    
    if warehouse_id:
        query = query.filter(Warehouse.id == warehouse_id)
    
    results = query.all()
    
    summary = []
    for row in results:
        summary.append({
            'warehouse_id': row.id,
            'warehouse_name': row.name,
            'warehouse_code': row.code,
            'product_count': row.product_count,
            'total_on_hand': row.total_on_hand or 0,
            'total_reserved': row.total_reserved or 0,
            'total_available': row.total_available or 0
        })
    
    return jsonify({'inventory_summary': summary})

@reports_bp.route('/movement-summary', methods=['GET'])
@jwt_required()
def movement_summary():
    """Get stock movement summary by product"""
    days = request.args.get('days', 30, type=int)
    product_id = request.args.get('product_id', type=int)
    warehouse_id = request.args.get('warehouse_id', type=int)
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Get IN movements
    in_query = db.session.query(
        Product.id, Product.sku, Product.name,
        func.sum(StockMovement.quantity).label('total_in')
    ).join(StockMovement).filter(
        and_(
            StockMovement.direction == MovementDirection.IN,
            StockMovement.created_at >= start_date
        )
    ).group_by(Product.id, Product.sku, Product.name)
    
    # Get OUT movements
    out_query = db.session.query(
        Product.id, Product.sku, Product.name,
        func.sum(StockMovement.quantity).label('total_out')
    ).join(StockMovement).filter(
        and_(
            StockMovement.direction == MovementDirection.OUT,
            StockMovement.created_at >= start_date
        )
    ).group_by(Product.id, Product.sku, Product.name)
    
    # Combine the results
    in_results = {row.id: {'sku': row.sku, 'name': row.name, 'total_in': row.total_in or 0} for row in in_query.all()}
    out_results = {row.id: {'sku': row.sku, 'name': row.name, 'total_out': row.total_out or 0} for row in out_query.all()}
    
    # Merge results
    all_product_ids = set(in_results.keys()) | set(out_results.keys())
    movement_summary = []
    
    for product_id in all_product_ids:
        in_data = in_results.get(product_id, {'sku': '', 'name': '', 'total_in': 0})
        out_data = out_results.get(product_id, {'sku': '', 'name': '', 'total_out': 0})
        
        movement_summary.append({
            'product_id': product_id,
            'sku': in_data['sku'] or out_data['sku'],
            'name': in_data['name'] or out_data['name'],
            'total_in': in_data['total_in'],
            'total_out': out_data['total_out'],
            'net_movement': in_data['total_in'] - out_data['total_out']
        })
    
    # Sort by total_out descending
    movement_summary.sort(key=lambda x: x['total_out'], reverse=True)
    
    return jsonify({'movement_summary': movement_summary})

@reports_bp.route('/purchase-summary', methods=['GET'])
@jwt_required()
def purchase_summary():
    """Get purchase order summary"""
    days = request.args.get('days', 30, type=int)
    supplier_id = request.args.get('supplier_id', type=int)
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Query with actual purchase values
    query = db.session.query(
        Supplier.id, Supplier.name,
        func.count(PurchaseOrder.id).label('order_count'),
        func.sum(PurchaseOrderLine.qty * PurchaseOrderLine.unit_price).label('total_value')
    ).outerjoin(PurchaseOrder, Supplier.id == PurchaseOrder.supplier_id).outerjoin(
        PurchaseOrderLine, PurchaseOrder.id == PurchaseOrderLine.purchase_order_id
    ).filter(
        PurchaseOrder.order_date >= start_date
    ).group_by(Supplier.id, Supplier.name)
    
    if supplier_id:
        query = query.filter(Supplier.id == supplier_id)
    
    results = query.all()
    
    purchase_summary = []
    for row in results:
        purchase_summary.append({
            'supplier_id': row.id,
            'supplier_name': row.name,
            'order_count': row.order_count,
            'total_value': float(row.total_value or 0)
        })
    
    return jsonify({'purchase_summary': purchase_summary})

@reports_bp.route('/sales-summary', methods=['GET'])
@jwt_required()
def sales_summary():
    """Get sales order summary"""
    days = request.args.get('days', 30, type=int)
    customer_id = request.args.get('customer_id', type=int)
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Simplified query without complex joins for now
    query = db.session.query(
        Customer.id, Customer.name,
        func.count(SalesOrder.id).label('order_count')
    ).outerjoin(SalesOrder, Customer.id == SalesOrder.customer_id).filter(
        SalesOrder.order_date >= start_date
    ).group_by(Customer.id, Customer.name)
    
    if customer_id:
        query = query.filter(Customer.id == customer_id)
    
    results = query.all()
    
    sales_summary = []
    for row in results:
        sales_summary.append({
            'customer_id': row.id,
            'customer_name': row.name,
            'order_count': row.order_count,
            'total_value': 0.0  # Simplified for now
        })
    
    return jsonify({'sales_summary': sales_summary})

@reports_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard_data():
    """Get dashboard summary data"""
    # Low stock count
    low_stock_count = db.session.query(InventoryBalance).join(Product).filter(
        InventoryBalance.available_qty <= Product.reorder_point
    ).count()
    
    # Total products
    total_products = Product.query.count()
    
    # Total warehouses
    total_warehouses = Warehouse.query.count()
    
    # Recent movements (last 7 days)
    recent_movements = StockMovement.query.filter(
        StockMovement.created_at >= datetime.now() - timedelta(days=7)
    ).count()
    
    # Pending purchase orders
    from app.models.purchase_order import PurchaseOrderStatus
    from app.models.sales_order import SalesOrderStatus
    
    pending_purchase_orders = PurchaseOrder.query.filter(
        PurchaseOrder.status.in_([PurchaseOrderStatus.DRAFT, PurchaseOrderStatus.APPROVED])
    ).count()
    
    # Pending sales orders
    pending_sales_orders = SalesOrder.query.filter(
        SalesOrder.status.in_([SalesOrderStatus.DRAFT, SalesOrderStatus.APPROVED])
    ).count()
    
    # Total purchase value (last 30 days)
    start_date = datetime.now() - timedelta(days=30)
    total_purchase_value = db.session.query(
        func.sum(PurchaseOrderLine.qty * PurchaseOrderLine.unit_price)
    ).join(PurchaseOrder).filter(
        PurchaseOrder.order_date >= start_date
    ).scalar() or 0
    
    return jsonify({
        'low_stock_count': low_stock_count,
        'total_products': total_products,
        'total_warehouses': total_warehouses,
        'recent_movements': recent_movements,
        'pending_purchase_orders': pending_purchase_orders,
        'pending_sales_orders': pending_sales_orders,
        'total_purchase_value': float(total_purchase_value)
    })
