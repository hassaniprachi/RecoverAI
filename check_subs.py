
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("Client_id")
SECRET = os.getenv("Secret_id")
BASE_URL = os.getenv("PAYPAL_BASE_URL")

# Check environment variables
if not CLIENT_ID or not SECRET or not BASE_URL:
    print("Missing PayPal credentials or BASE_URL in .env")
    raise SystemExit

# Get access token
auth = requests.post(
    BASE_URL + "/v1/oauth2/token",
    auth=(CLIENT_ID, SECRET),
    data={"grant_type": "client_credentials"}
)

if auth.status_code != 200:
    print("Authentication failed:", auth.text)
    raise SystemExit

token = auth.json()["access_token"]
print("PayPal Authentication Successful!")


# Check existing Billing Plan
plan_id = "P-1G9662394C162310CNLXNFGY"

response = requests.get(
    BASE_URL + "/v1/billing/plans/" + plan_id,
    headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
)

print("\nPlan Status Code:", response.status_code)

if response.status_code == 200:
    details = response.json()
    print("Plan ID:", details.get("id"))
    print("Plan Name:", details.get("name"))
    print("Plan Status:", details.get("status"))
else:
    print("Plan lookup failed:")
    print(response.text)

subscription_id = "I-D6W97LMFUN5V"

sub_response = requests.get(
    BASE_URL + "/v1/billing/subscriptions/" + subscription_id,
    headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
)

print("\nSubscription Status Code:", sub_response.status_code)

if sub_response.status_code == 200:
    sub = sub_response.json()
    print("Subscription ID:", sub.get("id"))
    print("Subscription Status:", sub.get("status"))
    print("Next Billing Time:", sub.get("billing_info", {}).get("next_billing_time"))
    print("Last Payment:", sub.get("billing_info", {}).get("last_payment"))
else:
    print(sub_response.text)