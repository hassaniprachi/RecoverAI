
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

# Create subscription
url = BASE_URL + "/v1/billing/subscriptions"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + access_token
}

subscription_data = {
    "plan_id": "P-4KM321859M4270615NLVAB6Q",
    "application_context": {
        "brand_name": "RecoverAI",
        "locale": "en-US",
        "user_action": "SUBSCRIBE_NOW",
        "payment_method": {
            "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
        },
        "return_url": "https://almanac-thesis-backpack.ngrok-free.dev/success",
        "cancel_url": "https://almanac-thesis-backpack.ngrok-free.dev/cancel"
    }
}

response = requests.post(
    url,
    headers=headers,
    json=subscription_data
)

if response.status_code in [200, 201]:
    subscription = response.json()

    print("Subscription Created Successfully!")
    print("Subscription ID:", subscription["id"])
    print("Status:", subscription["status"])

    for link in subscription.get("links", []):
        if link["rel"] == "approve":
            print("Approval Link:", link["href"])
else:
    print("Subscription creation failed!")
    print("Status:", response.status_code)
    print("Error:", response.text)
