
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("Client_id")
SECRET = os.getenv("Secret_id")
BASE_URL = os.getenv("PAYPAL_BASE_URL")

PLAN_ID = "P-4KM321859M4270615NLVAB6Q"

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

# Retrieve existing billing plan
response = requests.get(
    BASE_URL + "/v1/billing/plans/" + PLAN_ID,
    headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
)

print("Status Code:", response.status_code)

if response.status_code == 200:
    plan = response.json()

    print("Plan Name:", plan.get("name"))
    print("Plan ID:", plan.get("id"))
    print("Plan Status:", plan.get("status"))
    print("Billing Cycles:", plan.get("billing_cycles"))
else:
    print("Error:", response.text)
