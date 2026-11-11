
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("Client_id")
SECRET = os.getenv("Secret_id")
BASE_URL = os.getenv("PAYPAL_BASE_URL")

# Get access token
auth_response = requests.post(
    BASE_URL + "/v1/oauth2/token",
    auth=(CLIENT_ID, SECRET),
    data={"grant_type": "client_credentials"}
)

if auth_response.status_code != 200:
    print("Authentication failed!")
    print(auth_response.text)
    exit()

access_token = auth_response.json()["access_token"]

# Create billing plan
url = BASE_URL + "/v1/billing/plans"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + access_token
}

plan_data = {
    "product_id": "PROD-29D00820NR899571H",
    "name": "RecoverAI Monthly",
    "description": "Monthly subscription for RecoverAI Premium",
    "billing_cycles": [
        {
            "frequency": {
                "interval_unit": "MONTH",
                "interval_count": 1
            },
            "tenure_type": "REGULAR",
            "sequence": 1,
            "total_cycles": 0,
            "pricing_scheme": {
                "fixed_price": {
                    "value": "10.00",
                    "currency_code": "USD"
                }
            }
        }
    ],
    "payment_preferences": {
        "auto_bill_outstanding": True,
        "payment_failure_threshold": 3
    }
}

response = requests.post(
    url,
    headers=headers,
    json=plan_data
)

if response.status_code in [200, 201]:
    plan = response.json()

    print("Billing Plan Created Successfully!")
    print("Plan ID:", plan["id"])
    print("Plan Status:", plan["status"])

else:
    print("Plan creation failed!")
    print("Status:", response.status_code)
    print("Error:", response.text)
