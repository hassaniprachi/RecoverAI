
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

base_url = os.getenv("PAYPAL_BASE_URL")
client_id = os.getenv("Client_id")
secret = os.getenv("Secret_id")

token_response = requests.post(
    f"{base_url}/v1/oauth2/token",
    auth=HTTPBasicAuth(client_id, secret),
    data={"grant_type": "client_credentials"}
)

token = token_response.json()["access_token"]

response = requests.get(
    f"{base_url}/v1/billing/subscriptions/I-D6W97LMFUN5V",
    headers={"Authorization": f"Bearer {token}"}
)

print("Status Code:", response.status_code)

data = response.json()

print("Subscription ID:", data.get("id"))
print("Status:", data.get("status"))
print("Plan ID:", data.get("plan_id"))
print("Status Details:", data.get("status_update_time"))
print("Links:", data.get("links"))
