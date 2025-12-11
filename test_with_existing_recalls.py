#!/usr/bin/env python3
"""
Test ERPNext integration with existing recalls from database
Sends the 10 most recent recalls to ERPNext to check for inventory matches
"""
import requests
import json
from datetime import datetime
from database import db
from models import FDADeviceRecall
from app import app

# ERPNext Configuration
ERPNEXT_URL = "https://beta.surgi.shop/api/method/check_recall_inventory"
ERPNEXT_API_KEY = "ae0d7bdc5c61e8b"
ERPNEXT_API_SECRET = "c637ae040a3eae7"

def test_erpnext_with_existing_recalls(limit=10):
    """Send existing recalls to ERPNext for testing"""
    
    with app.app_context():
        # Get most recent recalls
        recent_recalls = FDADeviceRecall.query.order_by(
            FDADeviceRecall.recall_date.desc()
        ).limit(limit).all()
        
        if not recent_recalls:
            print("No recalls found in database!")
            return
        
        print("=" * 70)
        print(f"Testing ERPNext Integration with {len(recent_recalls)} Recent Recalls")
        print("=" * 70)
        print()
        
        # Format recalls for ERPNext
        formatted_recalls = []
        for recall in recent_recalls:
            print(f"Including: {recall.recall_number} - {recall.device_name[:50]}")
            formatted_recalls.append({
                'id': recall.id,
                'recall_number': recall.recall_number,
                'device_name': recall.device_name,
                'product_code': recall.product_code,
                'code_info': recall.code_info,
                'recall_date': recall.recall_date.isoformat() if recall.recall_date else None,
                'status': recall.status,
                'reason': recall.reason
            })
        
        print()
        print("Sending to ERPNext...")
        print("-" * 70)
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'token {ERPNEXT_API_KEY}:{ERPNEXT_API_SECRET}'
            }
            
            response = requests.post(
                ERPNEXT_URL,
                headers=headers,
                json={'recalls': formatted_recalls},  # Send as list, not JSON string
                timeout=60
            )
            
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                result = response.json()
                print("✓ SUCCESS!")
                print()
                print("Response:")
                print(json.dumps(result, indent=2))
                print()
                
                message = result.get('message', {})
                matched_count = message.get('matched_count', 0)
                
                print("=" * 70)
                print(f"MATCHES FOUND: {matched_count}")
                print("=" * 70)
                
                if matched_count > 0:
                    print()
                    print("Matched Items:")
                    for match in message.get('matches', []):
                        print(f"  • Recall: {match.get('recall_number')}")
                        print(f"    Item: {match.get('item_name')} ({match.get('item_code')})")
                        print(f"    Match Type: {match.get('match_type')}")
                        if match.get('batch_number'):
                            print(f"    Batch: {match.get('batch_number')}")
                        print()
                    
                    print("✉ Email notification should have been sent to gary.starr@surgishop.com")
                else:
                    print()
                    print("No inventory matches found in ERPNext.")
                    print("This means none of these recalls match your Item Names or Batch UDIs.")
                
                print("=" * 70)
                
            else:
                print("✗ ERROR!")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"✗ EXCEPTION!")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_erpnext_with_existing_recalls(limit=10)
