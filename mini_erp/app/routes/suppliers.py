from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Supplier
from marshmallow import Schema, fields, ValidationError

suppliers_bp = Blueprint('suppliers', __name__)

class SupplierSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    tax_no = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    is_active = fields.Bool(load_default=True)

supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)

@suppliers_bp.route('/', methods=['GET'])
@jwt_required()
def get_suppliers():
    suppliers = Supplier.query.all()
    return jsonify({'suppliers': suppliers_schema.dump(suppliers)})

@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    return jsonify({'supplier': supplier_schema.dump(supplier)})

@suppliers_bp.route('/', methods=['POST'])
@jwt_required()
def create_supplier():
    try:
        data = supplier_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Check if tax_no already exists
    if data.get('tax_no') and Supplier.query.filter_by(tax_no=data['tax_no']).first():
        return jsonify({'error': 'Tax number already exists'}), 400
    
    supplier = Supplier(**data)
    db.session.add(supplier)
    db.session.commit()
    
    return jsonify({'supplier': supplier_schema.dump(supplier)}), 201

@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
@jwt_required()
def update_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    try:
        data = supplier_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Check tax_no uniqueness
    if 'tax_no' in data and data['tax_no'] != supplier.tax_no:
        if data['tax_no'] and Supplier.query.filter_by(tax_no=data['tax_no']).first():
            return jsonify({'error': 'Tax number already exists'}), 400
    
    for key, value in data.items():
        setattr(supplier, key, value)
    
    db.session.commit()
    
    return jsonify({'supplier': supplier_schema.dump(supplier)})

@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Check if supplier has purchase orders
    if supplier.purchase_orders.count() > 0:
        return jsonify({'error': 'Cannot delete supplier with purchase orders'}), 400
    
    db.session.delete(supplier)
    db.session.commit()
    
    return jsonify({'message': 'Supplier deleted successfully'})
