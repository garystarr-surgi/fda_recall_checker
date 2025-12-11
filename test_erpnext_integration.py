import requests
import json

# Test data with realistic recall information
test_recalls = [
    {
        'recall_number': 'Z-TEST-2024-001',
        'device_name': 'Test Surgical Device',
        'product_code': 'TEST-PRODUCT-123',
        'code_info': 'UDI: 12345678901234\nGTIN: 98765432109876',
        'recall_date': '2024-12-11',
        'status': 'Ongoing',
        'reason': 'Test recall for integration verification',
        'id': 999999
    }
]

# ERPNext API endpoint
url = 'https://beta.surgi.shop/api/method/check_recall_inventory'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'token ae0d7bdc5c61e8b:c637ae040a3eae7'
}

print("=" * 60)
print("Testing ERPNext Recall Integration")
print("=" * 60)
print(f"\nSending {len(test_recalls)} test recall(s) to ERPNext...")

try:
    response = requests.post(
        url,
        headers=headers,
        json={'recalls': json.dumps(test_recalls)},
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ SUCCESS!")
        print(f"\nResponse:")
        print(json.dumps(result, indent=2))
        
        message = result.get('message', {})
        matched_count = message.get('matched_count', 0)
        
        print(f"\n{'='*60}")
        print(f"Matches Found: {matched_count}")
        
        if matched_count > 0:
            print("\nMatched Items:")
            for match in message.get('matches', []):
                print(f"  - {match.get('item_name')} ({match.get('item_code')})")
                print(f"    Match Type: {match.get('match_type')}")
                if match.get('batch_number'):
                    print(f"    Batch: {match.get('batch_number')}")
        else:
            print("\nNo inventory matches found (this is expected for test data)")
        
        print(f"{'='*60}")
        
    else:
        print(f"\n✗ ERROR!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n✗ EXCEPTION!")
    print(f"Error: {str(e)}")
