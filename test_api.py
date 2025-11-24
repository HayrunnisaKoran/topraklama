"""Test API endpoint"""
import requests
import json

try:
    r = requests.get('http://localhost:5000/api/realtime-data')
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Count: {data.get('count', 0)}")
    print(f"Message: {data.get('message', 'N/A')}")
    print(f"Source: {data.get('source', 'N/A')}")
    
    if data.get('data'):
        first = data['data'][0]
        print(f"\nFirst transformer:")
        print(f"  ID: {first.get('transformer_id')}")
        print(f"  Name: {first.get('name')}")
        print(f"  Risk Score: {first.get('risk_score')}")
        print(f"  Risk Level: {first.get('risk_level')}")
    else:
        print("\nNo data in response")
        
except Exception as e:
    print(f"Error: {e}")
