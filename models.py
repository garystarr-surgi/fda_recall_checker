"""
Database models for FDA Recall Checker
"""
from database import db
from datetime import datetime

class FDADeviceRecall(db.Model):
    """FDA Device Recall model"""
    __tablename__ = 'fda_device_recall'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True)
    recall_number = db.Column(db.String(200), unique=True, nullable=False, index=True)
    device_name = db.Column(db.String(140))
    manufacturer = db.Column(db.String(200))
    product_code = db.Column(db.String(100), index=True)
    recall_date = db.Column(db.Date, index=True)
    reason = db.Column(db.String(140))
    status = db.Column(db.String(100), index=True)
    recall_firm = db.Column(db.String(200))
    code_info = db.Column(db.String(140))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FDADeviceRecall {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'recall_number': self.recall_number,
            'device_name': self.device_name,
            'manufacturer': self.manufacturer,
            'product_code': self.product_code,
            'recall_date': self.recall_date.isoformat() if self.recall_date else None,
            'reason': self.reason,
            'status': self.status,
            'recall_firm': self.recall_firm,
            'code_info': self.code_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RecallCheckHistory(db.Model):
    """History of recall checks against ERPNext inventory"""
    __tablename__ = 'recall_check_history'
    
    id = db.Column(db.Integer, primary_key=True)
    check_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    new_recalls_count = db.Column(db.Integer, default=0)
    inventory_checked = db.Column(db.Boolean, default=False)
    matches_found = db.Column(db.Integer, default=0)
    notes = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<RecallCheckHistory {self.check_date} - {self.matches_found} matches>'

