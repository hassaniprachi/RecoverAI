
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

CLIENT_ID = os.getenv("Client_id")
SECRET = os.getenv("Secret_id")
BASE_URL = os.getenv("PAYPAL_BASE_URL")

# Get PayPal access token
token_response = requests.post(
    f"{BASE_URL}/v1/oauth2/token",
    auth=HTTPBasicAuth(CLIENT_ID, SECRET),
    data={"grant_type": "client_credentials"}
)

print("Authentication Status:", token_response.status_code)

if token_response.status_code != 200:
    print(token_response.text)
    exit()

access_token = token_response.json()["access_token"]

# List subscriptions for the RecoverAI plan
response = requests.get(
    f"{BASE_URL}/v1/billing/subscriptions",
    headers={"Authorization": f"Bearer {access_token}"},
    params={
        "plan_ids": "P-1G9662394C162310CNLXNFGY",
        "page_size": 20,
        "page": 1
    }
)

print("\nSubscription List Status:", response.status_code)

data = response.json()

if response.status_code == 200:
    subscriptions = data.get("subscriptions", [])

    if not subscriptions:
        print("No subscriptions found for this plan.")
    else:
        for sub in subscriptions:
            print("\nSubscription ID:", sub.get("id"))
            print("Status:", sub.get("status"))
            print("Subscriber:", sub.get("subscriber", {}).get("email_address"))
else:
    print(data)
