from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Product
from marshmallow import Schema, fields, ValidationError

products_bp = Blueprint('products', __name__)

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str(required=True)
    name = fields.Str(required=True)
    category = fields.Str(allow_none=True)
    unit = fields.Str(required=True)
    barcode = fields.Str(allow_none=True)
    reorder_point = fields.Int(load_default=0)
    safety_stock = fields.Int(load_default=0)
    is_active = fields.Bool(load_default=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@products_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    query = Product.query
    
    if search:
        query = query.filter(
            (Product.name.contains(search)) |
            (Product.sku.contains(search)) |
            (Product.barcode.contains(search))
        )
    
    products = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'products': products_schema.dump(products.items),
        'total': products.total,
        'pages': products.pages,
        'current_page': page
    })

@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({'product': product_schema.dump(product)})

@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    try:
        data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Check if SKU already exists
    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({'error': 'SKU already exists'}), 400
    
    # Check if barcode already exists
    if data.get('barcode') and Product.query.filter_by(barcode=data['barcode']).first():
        return jsonify({'error': 'Barcode already exists'}), 400
    
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    
    return jsonify({'product': product_schema.dump(product)}), 201

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    try:
        data = product_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Check SKU uniqueness
    if 'sku' in data and data['sku'] != product.sku:
        if Product.query.filter_by(sku=data['sku']).first():
            return jsonify({'error': 'SKU already exists'}), 400
    
    # Check barcode uniqueness
    if 'barcode' in data and data['barcode'] != product.barcode:
        if data['barcode'] and Product.query.filter_by(barcode=data['barcode']).first():
            return jsonify({'error': 'Barcode already exists'}), 400
    
    for key, value in data.items():
        setattr(product, key, value)
    
    db.session.commit()
    
    return jsonify({'product': product_schema.dump(product)})

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if product has stock movements
    if product.stock_movements.count() > 0:
        return jsonify({'error': 'Cannot delete product with stock movements'}), 400
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'})
