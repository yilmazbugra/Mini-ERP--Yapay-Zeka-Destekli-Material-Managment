from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Customer
from marshmallow import Schema, fields, ValidationError

customers_bp = Blueprint('customers', __name__)

class CustomerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    tax_no = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    is_active = fields.Bool(load_default=True)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

@customers_bp.route('/', methods=['GET'])
@jwt_required()
def get_customers():
    customers = Customer.query.all()
    return jsonify({'customers': customers_schema.dump(customers)})

@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({'customer': customer_schema.dump(customer)})

@customers_bp.route('/', methods=['POST'])
@jwt_required()
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Check if tax_no already exists
    if data.get('tax_no') and Customer.query.filter_by(tax_no=data['tax_no']).first():
        return jsonify({'error': 'Tax number already exists'}), 400
    
    customer = Customer(**data)
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({'customer': customer_schema.dump(customer)}), 201

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    try:
        data = customer_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Check tax_no uniqueness
    if 'tax_no' in data and data['tax_no'] != customer.tax_no:
        if data['tax_no'] and Customer.query.filter_by(tax_no=data['tax_no']).first():
            return jsonify({'error': 'Tax number already exists'}), 400
    
    for key, value in data.items():
        setattr(customer, key, value)
    
    db.session.commit()
    
    return jsonify({'customer': customer_schema.dump(customer)})

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    # Check if customer has sales orders
    if customer.sales_orders.count() > 0:
        return jsonify({'error': 'Cannot delete customer with sales orders'}), 400
    
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({'message': 'Customer deleted successfully'})
