"""
AI Dashboard Routes
Handles AI-powered analytics and predictions
"""

from flask import Blueprint, render_template, jsonify, request, session
from app.services.ml_service import MLService
from app.models import User

ai_dashboard_bp = Blueprint('ai_dashboard', __name__)

@ai_dashboard_bp.route('/ai-dashboard')
def ai_dashboard():
    """AI Dashboard main page"""
    return render_template('ai_dashboard.html')

@ai_dashboard_bp.route('/api/ai/summary')
def get_ai_summary():
    """Get AI dashboard summary data"""
    try:
        ml_service = MLService()
        summary = ml_service.get_ai_dashboard_summary()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        }), 500

@ai_dashboard_bp.route('/api/ai/predict-orders')
def predict_weekly_orders():
    """Predict orders for next week"""
    try:
        ml_service = MLService()
        result = ml_service.predict_weekly_orders()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        }), 500

@ai_dashboard_bp.route('/api/ai/customer-segmentation')
def customer_segmentation():
    """Perform customer segmentation"""
    try:
        ml_service = MLService()
        result = ml_service.perform_customer_segmentation()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        }), 500
