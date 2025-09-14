from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import (
    PurchaseOrder, PurchaseOrderLine, SalesOrder, SalesOrderLine,
    Supplier, Customer, Product, Warehouse, StockMovement, InventoryBalance
)
from app.models.purchase_order import PurchaseOrderStatus
from app.models.sales_order import SalesOrderStatus
from app.models.stock_movement import MovementDirection, MovementType
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, date

orders_bp = Blueprint('orders', __name__)

# Purchase Order Schemas
class PurchaseOrderLineSchema(Schema):
    product_id = fields.Int(required=True)
    qty = fields.Int(required=True)
    unit_price = fields.Decimal(required=True)

class PurchaseOrderSchema(Schema):
    supplier_id = fields.Int(required=True)
    order_no = fields.Str(required=True)
    order_date = fields.Date(required=True)
    expected_date = fields.Date(allow_none=True)
    note = fields.Str(allow_none=True)
    lines = fields.Nested(PurchaseOrderLineSchema, many=True, load_default=[])

# Sales Order Schemas
class SalesOrderLineSchema(Schema):
    product_id = fields.Int(required=True)
    qty = fields.Int(required=True)
    unit_price = fields.Decimal(required=True)

class SalesOrderSchema(Schema):
    customer_id = fields.Int(required=True)
    order_no = fields.Str(required=True)
    order_date = fields.Date(required=True)
    expected_ship_date = fields.Date(allow_none=True)
    note = fields.Str(allow_none=True)
    lines = fields.Nested(SalesOrderLineSchema, many=True, load_default=[])

purchase_order_schema = PurchaseOrderSchema()
purchase_orders_schema = PurchaseOrderSchema(many=True)
sales_order_schema = SalesOrderSchema()
sales_orders_schema = SalesOrderSchema(many=True)

# Purchase Orders
@orders_bp.route('/purchase', methods=['GET'])
@jwt_required()
def get_purchase_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = PurchaseOrder.query
    
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(PurchaseOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Include supplier information and ensure ID is included
    orders_with_suppliers = []
    for order in orders.items:
        order_data = purchase_order_schema.dump(order)
        order_data['id'] = order.id  # Ensure ID is included
        order_data['status'] = order.status.value if hasattr(order.status, 'value') else str(order.status)
        order_data['supplier'] = {
            'id': order.supplier.id,
            'name': order.supplier.name
        } if order.supplier else None
        orders_with_suppliers.append(order_data)
    
    return jsonify({
        'orders': orders_with_suppliers,
        'total': orders.total,
        'pages': orders.pages,
        'current_page': page
    })

@orders_bp.route('/purchase', methods=['POST'])
@jwt_required()
def create_purchase_order():
    print(f"Received purchase order data: {request.json}")
    try:
        data = purchase_order_schema.load(request.json)
        print(f"Parsed data: {data}")
    except ValidationError as err:
        print(f"Validation error: {err.messages}")
        return jsonify({'error': err.messages}), 400
    
    # Check if supplier exists
    supplier = Supplier.query.get(data['supplier_id'])
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404
    
    # Check if order_no already exists
    if PurchaseOrder.query.filter_by(order_no=data['order_no']).first():
        return jsonify({'error': 'Order number already exists'}), 400
    
    # Create purchase order
    order = PurchaseOrder(
        supplier_id=data['supplier_id'],
        order_no=data['order_no'],
        order_date=data['order_date'],
        expected_date=data.get('expected_date'),
        note=data.get('note'),
        status=PurchaseOrderStatus.DRAFT
    )
    
    db.session.add(order)
    db.session.flush()  # Get the order ID
    
    # Create order lines
    for line_data in data['lines']:
        product = Product.query.get(line_data['product_id'])
        if not product:
            return jsonify({'error': f'Product {line_data["product_id"]} not found'}), 404
        
        line = PurchaseOrderLine(
            purchase_order_id=order.id,
            product_id=line_data['product_id'],
            qty=line_data['qty'],
            unit_price=line_data['unit_price']
        )
        db.session.add(line)
    
    db.session.commit()
    
    return jsonify({'order': purchase_order_schema.dump(order)}), 201

@orders_bp.route('/purchase/<int:order_id>/approve', methods=['POST'])
@jwt_required()
def approve_purchase_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    
    print(f"Order {order_id} current status: {order.status}")
    
    if order.status != PurchaseOrderStatus.DRAFT:
        return jsonify({'error': 'Only draft orders can be approved'}), 400
    
    order.status = PurchaseOrderStatus.APPROVED
    db.session.commit()
    
    print(f"Order {order_id} new status: {order.status}")
    
    return jsonify({'message': 'Purchase order approved', 'order': purchase_order_schema.dump(order)})

@orders_bp.route('/purchase/<int:order_id>', methods=['GET'])
@jwt_required()
def get_purchase_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    
    # Include supplier information and order lines
    order_data = purchase_order_schema.dump(order)
    order_data['status'] = order.status.value if hasattr(order.status, 'value') else str(order.status)
    order_data['supplier'] = {
        'id': order.supplier.id,
        'name': order.supplier.name
    } if order.supplier else None
    
    # Include order lines with product information
    lines_data = []
    for line in order.lines:
        line_data = {
            'id': line.id,
            'product_id': line.product_id,
            'qty': line.qty,
            'unit_price': float(line.unit_price),
            'received_qty': line.received_qty,
            'status': line.status,
            'product': {
                'id': line.product.id,
                'name': line.product.name,
                'sku': line.product.sku
            } if line.product else None
        }
        lines_data.append(line_data)
    
    order_data['lines'] = lines_data
    
    return jsonify({'order': order_data})

@orders_bp.route('/purchase/<int:order_id>/receive', methods=['POST'])
@jwt_required()
def receive_purchase_order(order_id):
    data = request.json
    print(f"Received data for order {order_id}:", data)
    
    line_id = data.get('line_id')
    received_qty = data.get('received_qty')
    warehouse_id = data.get('warehouse_id')
    
    print(f"Extracted values - line_id: {line_id}, received_qty: {received_qty}, warehouse_id: {warehouse_id}")
    
    if not all([line_id, received_qty, warehouse_id]):
        print("Missing required fields - line_id:", line_id, "received_qty:", received_qty, "warehouse_id:", warehouse_id)
        return jsonify({'error': 'Missing required fields'}), 400
    
    order = PurchaseOrder.query.get_or_404(order_id)
    line = PurchaseOrderLine.query.get_or_404(line_id)
    
    if order.status not in [PurchaseOrderStatus.APPROVED, PurchaseOrderStatus.PARTIALLY_RECEIVED]:
        return jsonify({'error': 'Order must be approved to receive goods'}), 400
    
    remaining_qty = line.qty - line.received_qty
    if received_qty > remaining_qty:
        return jsonify({'error': 'Received quantity exceeds remaining quantity'}), 400
    
    # Check if warehouse exists
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return jsonify({'error': 'Warehouse not found'}), 404
    
    # Create stock movement
    movement = StockMovement(
        product_id=line.product_id,
        warehouse_id=warehouse_id,
        direction=MovementDirection.IN,
        quantity=received_qty,
        movement_type=MovementType.PURCHASE,
        ref_document_no=order.order_no,
        ref_line_id=line.id,
        note=f"Purchase receipt - {order.order_no}",
        created_by=get_jwt_identity()
    )
    
    db.session.add(movement)
    
    # Update inventory balance
    balance = InventoryBalance.query.filter_by(
        product_id=line.product_id, warehouse_id=warehouse_id
    ).first()
    
    if not balance:
        balance = InventoryBalance(
            product_id=line.product_id,
            warehouse_id=warehouse_id,
            on_hand_qty=0,
            reserved_qty=0,
            available_qty=0
        )
        db.session.add(balance)
    
    balance.on_hand_qty += received_qty
    balance.update_available_qty()
    
    # Update order line
    line.received_qty += received_qty
    if line.received_qty >= line.qty:
        line.status = 'Received'
    
    # Update order status
    total_received = sum(line.received_qty for line in order.lines)
    total_qty = sum(line.qty for line in order.lines)
    
    if total_received >= total_qty:
        order.status = PurchaseOrderStatus.CLOSED
    else:
        order.status = PurchaseOrderStatus.PARTIALLY_RECEIVED
    
    db.session.commit()
    
    return jsonify({'message': 'Goods received successfully'})

# Sales Orders
@orders_bp.route('/sales', methods=['GET'])
@jwt_required()
def get_sales_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = SalesOrder.query
    
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(SalesOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Include customer information and ensure ID is included
    orders_with_customers = []
    for order in orders.items:
        order_data = sales_order_schema.dump(order)
        order_data['id'] = order.id  # Ensure ID is included
        order_data['status'] = order.status.value if hasattr(order.status, 'value') else str(order.status)
        order_data['customer'] = {
            'id': order.customer.id,
            'name': order.customer.name
        } if order.customer else None
        
        # Include order lines with product information
        lines_data = []
        for line in order.lines:
            line_data = {
                'id': line.id,
                'product_id': line.product_id,
                'qty': line.qty,
                'unit_price': float(line.unit_price),
                'shipped_qty': line.shipped_qty,
                'status': line.status,
                'product': {
                    'id': line.product.id,
                    'name': line.product.name,
                    'sku': line.product.sku
                } if line.product else None
            }
            lines_data.append(line_data)
        
        order_data['lines'] = lines_data
        orders_with_customers.append(order_data)
    
    return jsonify({
        'orders': orders_with_customers,
        'total': orders.total,
        'pages': orders.pages,
        'current_page': page
    })

@orders_bp.route('/sales', methods=['POST'])
@jwt_required()
def create_sales_order():
    try:
        data = sales_order_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Check if customer exists
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Check if order_no already exists
    if SalesOrder.query.filter_by(order_no=data['order_no']).first():
        return jsonify({'error': 'Order number already exists'}), 400
    
    # Create sales order
    order = SalesOrder(
        customer_id=data['customer_id'],
        order_no=data['order_no'],
        order_date=data['order_date'],
        expected_ship_date=data.get('expected_ship_date'),
        note=data.get('note'),
        status=SalesOrderStatus.DRAFT
    )
    
    db.session.add(order)
    db.session.flush()  # Get the order ID
    
    # Create order lines
    for line_data in data['lines']:
        product = Product.query.get(line_data['product_id'])
        if not product:
            return jsonify({'error': f'Product {line_data["product_id"]} not found'}), 404
        
        line = SalesOrderLine(
            sales_order_id=order.id,
            product_id=line_data['product_id'],
            qty=line_data['qty'],
            unit_price=line_data['unit_price']
        )
        db.session.add(line)
    
    db.session.commit()
    
    return jsonify({'order': sales_order_schema.dump(order)}), 201

@orders_bp.route('/sales/<int:order_id>/approve', methods=['POST'])
@jwt_required()
def approve_sales_order(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    
    print(f"Sales Order {order_id} current status: {order.status}")
    
    if order.status != SalesOrderStatus.DRAFT:
        return jsonify({'error': 'Only draft orders can be approved'}), 400
    
    order.status = SalesOrderStatus.APPROVED
    db.session.commit()
    
    print(f"Sales Order {order_id} new status: {order.status}")
    
    return jsonify({'message': 'Sales order approved', 'order': sales_order_schema.dump(order)})

@orders_bp.route('/sales/<int:order_id>/ship', methods=['POST'])
@jwt_required()
def ship_sales_order(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    
    if order.status != SalesOrderStatus.APPROVED:
        return jsonify({'error': 'Order must be approved to ship goods'}), 400
    
    # Get the first warehouse for simplicity
    warehouse = Warehouse.query.first()
    if not warehouse:
        return jsonify({'error': 'No warehouse found'}), 404
    
    # Ship all lines
    for line in order.lines:
        if line.shipped_qty < line.qty:
            remaining_qty = line.qty - line.shipped_qty
            
            # Check available stock
            balance = InventoryBalance.query.filter_by(
                product_id=line.product_id, warehouse_id=warehouse.id
            ).first()
            
            if not balance:
                # Create inventory balance if it doesn't exist
                balance = InventoryBalance(
                    product_id=line.product_id,
                    warehouse_id=warehouse.id,
                    on_hand_qty=0,
                    reserved_qty=0,
                    available_qty=0
                )
                db.session.add(balance)
                db.session.flush()
            
            # Create stock movement
            movement = StockMovement(
                product_id=line.product_id,
                warehouse_id=warehouse.id,
                direction=MovementDirection.OUT,
                quantity=remaining_qty,
                movement_type=MovementType.SALES,
                ref_document_no=order.order_no,
                ref_line_id=line.id,
                note=f"Sales shipment - {order.order_no}",
                created_by=get_jwt_identity()
            )
            
            db.session.add(movement)
            
            # Update inventory balance
            balance.on_hand_qty -= remaining_qty
            balance.update_available_qty()
            
            # Update order line
            line.shipped_qty = line.qty
            line.status = 'Shipped'
    
    # Update order status to CLOSED
    order.status = SalesOrderStatus.CLOSED
    db.session.commit()
    
    return jsonify({'message': 'Goods shipped successfully'})

@orders_bp.route('/sales/<int:order_id>', methods=['GET'])
@jwt_required()
def get_sales_order(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    
    # Include customer information and order lines
    order_data = sales_order_schema.dump(order)
    order_data['id'] = order.id
    order_data['status'] = order.status.value if hasattr(order.status, 'value') else str(order.status)
    order_data['customer'] = {
        'id': order.customer.id,
        'name': order.customer.name
    } if order.customer else None
    
    # Include order lines with product information
    lines_data = []
    for line in order.lines:
        line_data = {
            'id': line.id,
            'product_id': line.product_id,
            'qty': line.qty,
            'unit_price': float(line.unit_price),
            'shipped_qty': line.shipped_qty,
            'status': line.status,
            'product': {
                'id': line.product.id,
                'name': line.product.name,
                'sku': line.product.sku
            } if line.product else None
        }
        lines_data.append(line_data)
    
    order_data['lines'] = lines_data
    
    return jsonify({'order': order_data})
