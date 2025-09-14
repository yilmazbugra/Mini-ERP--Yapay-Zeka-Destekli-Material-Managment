from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Warehouse
from marshmallow import Schema, fields, ValidationError

warehouses_bp = Blueprint('warehouses', __name__)

class WarehouseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    code = fields.Str(required=True)
    address = fields.Str(allow_none=True)
    is_active = fields.Bool(load_default=True)

warehouse_schema = WarehouseSchema()
warehouses_schema = WarehouseSchema(many=True)

@warehouses_bp.route('/', methods=['GET'])
@jwt_required()
def get_warehouses():
    warehouses = Warehouse.query.all()
    return jsonify({'warehouses': warehouses_schema.dump(warehouses)})

@warehouses_bp.route('/<int:warehouse_id>', methods=['GET'])
@jwt_required()
def get_warehouse(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    return jsonify({'warehouse': warehouse_schema.dump(warehouse)})

@warehouses_bp.route('/', methods=['POST'])
@jwt_required()
def create_warehouse():
    try:
        data = warehouse_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Check if code already exists
    if Warehouse.query.filter_by(code=data['code']).first():
        return jsonify({'error': 'Warehouse code already exists'}), 400
    
    warehouse = Warehouse(**data)
    db.session.add(warehouse)
    db.session.commit()
    
    return jsonify({'warehouse': warehouse_schema.dump(warehouse)}), 201

@warehouses_bp.route('/<int:warehouse_id>', methods=['PUT'])
@jwt_required()
def update_warehouse(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    
    try:
        data = warehouse_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Check code uniqueness
    if 'code' in data and data['code'] != warehouse.code:
        if Warehouse.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Warehouse code already exists'}), 400
    
    for key, value in data.items():
        setattr(warehouse, key, value)
    
    db.session.commit()
    
    return jsonify({'warehouse': warehouse_schema.dump(warehouse)})

@warehouses_bp.route('/<int:warehouse_id>', methods=['DELETE'])
@jwt_required()
def delete_warehouse(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    
    # Check if warehouse has stock movements
    if warehouse.stock_movements.count() > 0:
        return jsonify({'error': 'Cannot delete warehouse with stock movements'}), 400
    
    db.session.delete(warehouse)
    db.session.commit()
    
    return jsonify({'message': 'Warehouse deleted successfully'})
