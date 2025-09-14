from flask import Blueprint, render_template, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')
    
@main_bp.route('/dashboard')
@jwt_required()
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/products')
@jwt_required()
def products():
    return render_template('products.html')

@main_bp.route('/warehouses')
@jwt_required()
def warehouses():
    return render_template('warehouses.html')

@main_bp.route('/inventory')
@jwt_required()
def inventory():
    return render_template('inventory.html')

@main_bp.route('/stock-movements')
@jwt_required()
def stock_movements():
    return render_template('stock_movements.html')

@main_bp.route('/purchase-orders')
@jwt_required()
def purchase_orders():
    return render_template('purchase_orders.html')

@main_bp.route('/sales-orders')
@jwt_required()
def sales_orders():
    return render_template('sales_orders.html')

@main_bp.route('/suppliers')
@jwt_required()
def suppliers():
    return render_template('suppliers.html')

@main_bp.route('/customers')
@jwt_required()
def customers():
    return render_template('customers.html')

@main_bp.route('/reports')
@jwt_required()
def reports():
    return render_template('reports.html')



@main_bp.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Mini ERP API is running'})

@main_bp.route('/api/dashboard')
@jwt_required()
def dashboard_api():
    # Dashboard data will be implemented later
    return jsonify({
        'message': 'Dashboard data',
        'user': get_jwt_identity()
    })

# Serve static files
@main_bp.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static'), filename)
