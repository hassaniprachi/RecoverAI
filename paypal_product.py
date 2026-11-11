import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("Client_id")
SECRET = os.getenv("Secret_id")
BASE_URL = os.getenv("PAYPAL_BASE_URL")


# Get access token
auth_url = BASE_URL + "/v1/oauth2/token"

auth_response = requests.post(
    auth_url,
    auth=(CLIENT_ID, SECRET),
    data={"grant_type": "client_credentials"}
)

print("Status Code:", auth_response.status_code)
print("PayPal Response:", auth_response.text)

if auth_response.status_code == 200:
    access_token = auth_response.json()["access_token"]
else:
    print("Authentication failed!")
    exit()

# Create product
product_url = BASE_URL + "/v1/catalogs/products"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + access_token
}

product_data = {
    "name": "RecoverAI Premium",
    "description": "Monthly subscription for RecoverAI testing",
    "type": "SERVICE",
    "category": "SOFTWARE"
}

response = requests.post(
    product_url,
    headers=headers,
    json=product_data
)

if response.status_code == 201:
    product = response.json()
    print("Product created successfully!")
    print("Product ID:", product["id"])
else:
    print("Product creation failed!")
    print(response.status_code)
    print(response.text)
