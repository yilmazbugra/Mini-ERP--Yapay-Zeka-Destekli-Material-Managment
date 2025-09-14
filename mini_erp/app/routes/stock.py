from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import StockMovement, InventoryBalance, Product, Warehouse, User
from app.models.stock_movement import MovementDirection, MovementType
from marshmallow import Schema, fields, ValidationError
from sqlalchemy.orm import joinedload
from datetime import datetime

stock_bp = Blueprint('stock', __name__)

class StockMovementSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    direction = fields.Str(required=True)
    quantity = fields.Int(required=True)
    movement_type = fields.Str(required=True)
    ref_document_no = fields.Str(allow_none=True)
    ref_line_id = fields.Int(allow_none=True)
    note = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int(dump_only=True)
    
    # Related data fields
    product = fields.Method('get_product_data')
    warehouse = fields.Method('get_warehouse_data')
    user = fields.Method('get_user_data')
    
    def get_product_data(self, obj):
        if hasattr(obj, 'product') and obj.product:
            return {
                'id': obj.product.id,
                'sku': obj.product.sku,
                'name': obj.product.name
            }
        return None
    
    def get_warehouse_data(self, obj):
        if hasattr(obj, 'warehouse') and obj.warehouse:
            return {
                'id': obj.warehouse.id,
                'name': obj.warehouse.name
            }
        return None
    
    def get_user_data(self, obj):
        if hasattr(obj, 'user') and obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username
            }
        return None

stock_movement_schema = StockMovementSchema()
stock_movements_schema = StockMovementSchema(many=True)

@stock_bp.route('/movements', methods=['GET'])
@jwt_required()
def get_stock_movements():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    product_id = request.args.get('product_id', type=int)
    warehouse_id = request.args.get('warehouse_id', type=int)
    movement_type = request.args.get('movement_type')
    
    query = StockMovement.query
    
    if product_id:
        query = query.filter_by(product_id=product_id)
    if warehouse_id:
        query = query.filter_by(warehouse_id=warehouse_id)
    if movement_type:
        query = query.filter_by(movement_type=movement_type)
    
    # Load related data
    movements = query.options(
        db.joinedload(StockMovement.product),
        db.joinedload(StockMovement.warehouse),
        db.joinedload(StockMovement.user)
    ).order_by(StockMovement.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'movements': stock_movements_schema.dump(movements.items),
        'total': movements.total,
        'pages': movements.pages,
        'current_page': page
    })

@stock_bp.route('/movements', methods=['POST'])
@jwt_required()
def create_stock_movement():
    try:
        data = stock_movement_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Validate product and warehouse exist
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    warehouse = Warehouse.query.get(data['warehouse_id'])
    if not warehouse:
        return jsonify({'error': 'Warehouse not found'}), 404
    
    # Validate direction and movement_type
    try:
        direction = MovementDirection(data['direction'])
        movement_type = MovementType(data['movement_type'])
    except ValueError:
        return jsonify({'error': 'Invalid direction or movement_type'}), 400
    
    # Create stock movement
    movement = StockMovement(
        product_id=data['product_id'],
        warehouse_id=data['warehouse_id'],
        direction=direction,
        quantity=data['quantity'],
        movement_type=movement_type,
        ref_document_no=data.get('ref_document_no'),
        ref_line_id=data.get('ref_line_id'),
        note=data.get('note'),
        created_by=get_jwt_identity()
    )
    
    db.session.add(movement)
    
    # Update inventory balance
    balance = InventoryBalance.query.filter_by(
        product_id=data['product_id'],
        warehouse_id=data['warehouse_id']
    ).first()
    
    if not balance:
        balance = InventoryBalance(
            product_id=data['product_id'],
            warehouse_id=data['warehouse_id'],
            on_hand_qty=0,
            reserved_qty=0,
            available_qty=0
        )
        db.session.add(balance)
    
    # Update quantities based on direction
    if direction == MovementDirection.IN:
        balance.on_hand_qty += data['quantity']
    else:  # OUT
        if balance.on_hand_qty < data['quantity']:
            return jsonify({'error': 'Insufficient stock'}), 400
        balance.on_hand_qty -= data['quantity']
    
    balance.update_available_qty()
    
    db.session.commit()
    
    return jsonify({'movement': stock_movement_schema.dump(movement)}), 201

@stock_bp.route('/inventory', methods=['GET'])
@jwt_required()
def get_inventory_balances():
    warehouse_id = request.args.get('warehouse_id', type=int)
    low_stock = request.args.get('low_stock', type=bool)
    
    query = InventoryBalance.query.join(Product).join(Warehouse)
    
    if warehouse_id:
        query = query.filter(InventoryBalance.warehouse_id == warehouse_id)
    
    if low_stock:
        query = query.filter(InventoryBalance.available_qty <= Product.reorder_point)
    
    balances = query.all()
    
    result = []
    for balance in balances:
        balance_data = {
            'id': balance.id,
            'product': {
                'id': balance.product.id,
                'sku': balance.product.sku,
                'name': balance.product.name,
                'unit': balance.product.unit,
                'reorder_point': balance.product.reorder_point,
                'safety_stock': balance.product.safety_stock
            },
            'warehouse': {
                'id': balance.warehouse.id,
                'name': balance.warehouse.name,
                'code': balance.warehouse.code
            },
            'on_hand_qty': balance.on_hand_qty,
            'reserved_qty': balance.reserved_qty,
            'available_qty': balance.available_qty,
            'is_low_stock': balance.available_qty <= balance.product.reorder_point
        }
        result.append(balance_data)
    
    return jsonify({'inventory_balances': result})

@stock_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer_stock():
    data = request.json
    product_id = data.get('product_id')
    from_warehouse_id = data.get('from_warehouse_id')
    to_warehouse_id = data.get('to_warehouse_id')
    quantity = data.get('quantity')
    note = data.get('note', '')
    
    if not all([product_id, from_warehouse_id, to_warehouse_id, quantity]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if from_warehouse_id == to_warehouse_id:
        return jsonify({'error': 'Source and destination warehouses cannot be the same'}), 400
    
    # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check if warehouses exist
    from_warehouse = Warehouse.query.get(from_warehouse_id)
    to_warehouse = Warehouse.query.get(to_warehouse_id)
    if not from_warehouse or not to_warehouse:
        return jsonify({'error': 'Warehouse not found'}), 404
    
    # Check available stock
    from_balance = InventoryBalance.query.filter_by(
        product_id=product_id, warehouse_id=from_warehouse_id
    ).first()
    
    if not from_balance or from_balance.available_qty < quantity:
        return jsonify({'error': 'Insufficient stock for transfer'}), 400
    
    # Create OUT movement
    out_movement = StockMovement(
        product_id=product_id,
        warehouse_id=from_warehouse_id,
        direction=MovementDirection.OUT,
        quantity=quantity,
        movement_type=MovementType.TRANSFER,
        ref_document_no=f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        note=f"Transfer to {to_warehouse.name}. {note}",
        created_by=get_jwt_identity()
    )
    
    # Create IN movement
    in_movement = StockMovement(
        product_id=product_id,
        warehouse_id=to_warehouse_id,
        direction=MovementDirection.IN,
        quantity=quantity,
        movement_type=MovementType.TRANSFER,
        ref_document_no=out_movement.ref_document_no,
        note=f"Transfer from {from_warehouse.name}. {note}",
        created_by=get_jwt_identity()
    )
    
    db.session.add(out_movement)
    db.session.add(in_movement)
    
    # Update from warehouse balance
    from_balance.on_hand_qty -= quantity
    from_balance.update_available_qty()
    
    # Update to warehouse balance
    to_balance = InventoryBalance.query.filter_by(
        product_id=product_id, warehouse_id=to_warehouse_id
    ).first()
    
    if not to_balance:
        to_balance = InventoryBalance(
            product_id=product_id,
            warehouse_id=to_warehouse_id,
            on_hand_qty=0,
            reserved_qty=0,
            available_qty=0
        )
        db.session.add(to_balance)
    
    to_balance.on_hand_qty += quantity
    to_balance.update_available_qty()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Stock transferred successfully',
        'out_movement': stock_movement_schema.dump(out_movement),
        'in_movement': stock_movement_schema.dump(in_movement)
    }), 201

