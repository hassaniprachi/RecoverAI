
import os
import requests
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

CLIENT_ID = os.getenv("Client_id")
SECRET = os.getenv("Secret_id")
BASE_URL = os.getenv("PAYPAL_BASE_URL")

# Check whether credentials exist
if not CLIENT_ID or not SECRET or not BASE_URL:
    print("PayPal credentials missing!")
    exit()

# PayPal OAuth API
url = BASE_URL + "/v1/oauth2/token"

# Send authentication request
response = requests.post(
    url,
    auth=(CLIENT_ID, SECRET),
    data={"grant_type": "client_credentials"}
)

# Check response
if response.status_code == 200:

    access_token = response.json()["access_token"]

    print("PayPal Authentication Successful!")
    print("Access Token received successfully.")

else:
    print("Authentication Failed!")
    print("Status Code:", response.status_code)
    print("Error:", response.json())
