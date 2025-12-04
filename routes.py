"""
Flask routes for FDA Recall Checker
"""
from flask import Blueprint, jsonify, request
from database import db
from models import FDADeviceRecall
from fetch_fda_recalls import fetch_fda_recalls
from datetime import datetime

fetch_recalls_bp = Blueprint('fetch_recalls', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

@fetch_recalls_bp.route('/fetch', methods=['POST', 'GET'])
def fetch_recalls():
    """Manually trigger FDA recall fetch"""
    try:
        result = fetch_fda_recalls()
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/recalls')
def api_recalls():
    """API endpoint to get recalls"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search', '', type=str)
    
    query = FDADeviceRecall.query
    
    if search:
        query = query.filter(
            db.or_(
                FDADeviceRecall.device_name.contains(search),
                FDADeviceRecall.recall_number.contains(search),
                FDADeviceRecall.recall_firm.contains(search)
            )
        )
    
    pagination = query.order_by(
        FDADeviceRecall.recall_date.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'recalls': [recall.to_dict() for recall in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@api_bp.route('/recalls/<int:recall_id>')
def api_recall_detail(recall_id):
    """API endpoint to get a specific recall"""
    recall = FDADeviceRecall.query.get_or_404(recall_id)
    return jsonify(recall.to_dict())

@api_bp.route('/stats')
def api_stats():
    """API endpoint for statistics"""
    total = FDADeviceRecall.query.count()
    by_status = db.session.query(
        FDADeviceRecall.status,
        db.func.count(FDADeviceRecall.id)
    ).group_by(FDADeviceRecall.status).all()
    
    recent_count = FDADeviceRecall.query.filter(
        FDADeviceRecall.recall_date >= datetime.now().replace(day=1)
    ).count()
    
    return jsonify({
        'total': total,
        'by_status': {status: count for status, count in by_status},
        'recent_count': recent_count
    })

