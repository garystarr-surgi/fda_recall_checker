"""
FDA Recall Checker - Standalone Flask Application
Main application entry point
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
from database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fda_recalls.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database with app
db.init_app(app)

# Import models and routes (after db initialization)
from models import FDADeviceRecall

# Register blueprints
from routes import fetch_recalls_bp, api_bp
app.register_blueprint(fetch_recalls_bp)
app.register_blueprint(api_bp)

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        total_recalls = FDADeviceRecall.query.count()
        recent_recalls = FDADeviceRecall.query.order_by(
            FDADeviceRecall.recall_date.desc()
        ).limit(10).all()
    except Exception as e:
        # Log error but don't crash
        import logging
        logging.error(f"Error querying recalls: {e}")
        total_recalls = 0
        recent_recalls = []
    
    return render_template('index.html', 
                         total_recalls=total_recalls,
                         recent_recalls=recent_recalls)

@app.route('/recalls')
def recalls():
    """List all recalls with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search', '', type=str)
    
    query = FDADeviceRecall.query
    
    if search:
        query = query.filter(
            db.or_(
                FDADeviceRecall.device_name.contains(search),
                FDADeviceRecall.recall_number.contains(search),
                FDADeviceRecall.recall_firm.contains(search),
                FDADeviceRecall.recall.product.code(search)
            )
        )
    
    pagination = query.order_by(
        FDADeviceRecall.recall_date.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('recalls.html',
                         recalls=pagination.items,
                         pagination=pagination,
                         search=search)

@app.route('/recall/<int:recall_id>')
def recall_detail(recall_id):
    """View details of a specific recall"""
    recall = FDADeviceRecall.query.get_or_404(recall_id)
    return render_template('recall_detail.html', recall=recall)

@app.route('/stats')
def stats():
    """Statistics page"""
    total = FDADeviceRecall.query.count()
    by_status = db.session.query(
        FDADeviceRecall.status,
        db.func.count(FDADeviceRecall.id)
    ).group_by(FDADeviceRecall.status).all()
    
    recent_count = FDADeviceRecall.query.filter(
        FDADeviceRecall.recall_date >= datetime.now().replace(day=1)
    ).count()
    
    return render_template('stats.html',
                         total=total,
                         by_status=by_status,
                         recent_count=recent_count)

# Initialize database
def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    # For development
    app.run(host='0.0.0.0', port=5000, debug=True)

