# test_uuid_payment.py
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_TOKEN = "your_jwt_token_here"
BOOKING_UUID = "19664e38-302f-4995-8ec2-a8b93991e076"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Test payment initiation
payload = {
    "booking_id": BOOKING_UUID
}

response = requests.post(f"{BASE_URL}/payments/", json=payload, headers=headers)
print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))