
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from google import genai
from pydantic import BaseModel

from urllib.parse import urlparse
import sqlite3
import requests
import os
import json
import base64
import zlib


load_dotenv()

app = FastAPI()

# CORS: Allow frontend to communicate with backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_ID = os.getenv("Client_id")
SECRET = os.getenv("Secret_id")
BASE_URL = os.getenv("PAYPAL_BASE_URL")
REAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SIMULATOR_WEBHOOK_ID = "WEBHOOK_ID"

certificate_cache = {}

# Initialize Gemini.
gemini_client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY else None
)


# ---------------- PAYPAL AUTHENTICATION ----------------

def get_access_token():

    response = requests.post(
        BASE_URL + "/v1/oauth2/token",
        auth=(CLIENT_ID, SECRET),
        data={"grant_type": "client_credentials"},
        timeout=15
    )

    response.raise_for_status()

    return response.json()["access_token"]


# ---------------- CERTIFICATE VERIFICATION ----------------

def get_certificate(cert_url):

    parsed_url = urlparse(cert_url)
    hostname = parsed_url.hostname or ""

    if parsed_url.scheme != "https" or not (
        hostname == "paypal.com"
        or hostname.endswith(".paypal.com")
    ):
        raise ValueError("Invalid PayPal certificate URL")

    if cert_url not in certificate_cache:

        response = requests.get(cert_url, timeout=15)
        response.raise_for_status()

        certificate_cache[cert_url] = (
            x509.load_pem_x509_certificate(response.content)
        )

    return certificate_cache[cert_url]


def verify_local_signature(headers, raw_body, webhook_id):

    transmission_id = headers.get("paypal-transmission-id")
    transmission_time = headers.get("paypal-transmission-time")
    transmission_sig = headers.get("paypal-transmission-sig")
    cert_url = headers.get("paypal-cert-url")
    auth_algo = headers.get("paypal-auth-algo")

    if not all([
        transmission_id,
        transmission_time,
        transmission_sig,
        cert_url,
        auth_algo
    ]):
        return False

    if auth_algo != "SHA256withRSA":
        return False

    crc = zlib.crc32(raw_body) & 0xFFFFFFFF

    message = (
        f"{transmission_id}|"
        f"{transmission_time}|"
        f"{webhook_id}|"
        f"{crc}"
    )

    certificate = get_certificate(cert_url)

    signature = base64.b64decode(
        transmission_sig,
        validate=True
    )

    try:

        certificate.public_key().verify(
            signature,
            message.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return True

    except InvalidSignature:
        return False


# Official PayPal verification.
def verify_real_paypal_event(headers, event):

    access_token = get_access_token()

    verification_data = {
        "auth_algo": headers.get("paypal-auth-algo"),
        "cert_url": headers.get("paypal-cert-url"),
        "transmission_id": headers.get("paypal-transmission-id"),
        "transmission_sig": headers.get("paypal-transmission-sig"),
        "transmission_time": headers.get("paypal-transmission-time"),
        "webhook_id": REAL_WEBHOOK_ID,
        "webhook_event": event
    }

    response = requests.post(
        BASE_URL + "/v1/notifications/verify-webhook-signature",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token
        },
        json=verification_data,
        timeout=20
    )

    response.raise_for_status()

    return (
        response.json().get("verification_status") == "SUCCESS"
    )


# ---------------- DATABASE ----------------

def initialize_database():

    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(webhook_events)")
    columns = [row[1] for row in cursor.fetchall()]

    if "resource_json" not in columns:

        cursor.execute("""
            ALTER TABLE webhook_events
            ADD COLUMN resource_json TEXT
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_recommendations (
            event_id TEXT PRIMARY KEY,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id)
                REFERENCES webhook_events(event_id)
        )
    """)

    conn.commit()
    conn.close()




def save_event(event):

    event_id = event.get("id")
    event_type = event.get("event_type")
    resource = event.get("resource") or {}

    print("\n===== INCOMING WEBHOOK RESOURCE =====")
    print(json.dumps(resource, indent=4))
    print("======================================\n")

    if not event_id or not event_type:
        raise ValueError("Event ID or event type is missing")

    # Extract subscription ID from PayPal event
    supplementary_data = resource.get("supplementary_data") or {}
    related_ids = supplementary_data.get("related_ids") or {}

    subscription_id = (
        resource.get("billing_agreement_id")
        or resource.get("subscription_id")
        or related_ids.get("billing_agreement_id")
    )

    if not subscription_id and event_type.startswith("BILLING.SUBSCRIPTION."):
        subscription_id = resource.get("id")

    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    try:
        # Check whether this event already exists
        cursor.execute("""
            SELECT resource_json, subscription_id
            FROM webhook_events
            WHERE event_id = ?
        """, (event_id,))

        existing = cursor.fetchone()
        is_new_event = existing is None

        if existing:
            existing_resource, existing_subscription_id = existing

            # Reuse previously saved subscription ID if necessary
            if not subscription_id:
                subscription_id = existing_subscription_id

            # Update missing event details
            if (
    not existing_resource
    or existing_resource == "{}"
    or (not existing_subscription_id and subscription_id)
):
                cursor.execute("""
                    UPDATE webhook_events
                    SET resource_json = ?,
                        subscription_id = ?
                    WHERE event_id = ?
                """, (
                    json.dumps(resource),
                    subscription_id,
                    event_id
                ))

                conn.commit()
                print("Existing event resource updated!")

            else:
                print("Duplicate event received. Checking recovery...")

        else:
            # Save new event
            cursor.execute("""
                INSERT INTO webhook_events
                (event_id, event_type, subscription_id, resource_json)
                VALUES (?, ?, ?, ?)
            """, (
                event_id,
                event_type,
                subscription_id,
                json.dumps(resource)
            ))

            conn.commit()
            print("New event saved successfully!")

        # Update recovery status after confirmed successful payment
        if event_type in (
    "PAYMENT.SALE.COMPLETED",
    "BILLING.SUBSCRIPTION.PAYMENT.COMPLETED"
) and subscription_id:

            cursor.execute("""
                UPDATE webhook_events
                SET recovery_status = 'Recovered',
                    recovered_at = CURRENT_TIMESTAMP
                WHERE id = (
                    SELECT id
                    FROM webhook_events
                    WHERE subscription_id = ?
                    AND event_type = 'BILLING.SUBSCRIPTION.PAYMENT.FAILED'
                    ORDER BY id DESC
                    LIMIT 1
                )
            """, (subscription_id,))

            conn.commit()

            if cursor.rowcount == 1:
                print("Payment recovered! Recovery status updated.")
            else:
                print("No matching failed payment found.")

        elif event_type in (
    "PAYMENT.SALE.COMPLETED",
    "BILLING.SUBSCRIPTION.PAYMENT.COMPLETED"
     ):

         print("Payment completed event received, but subscription ID is missing.")
        return is_new_event

    finally:
        conn.close()



# ---------------- GEMINI AI ----------------


def analyze_failed_payment(event):

    if not gemini_client:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    resource = event.get("resource") or {}

    billing_info = resource.get("billing_info") or {}
    failed_payment = billing_info.get("last_failed_payment") or {}
    amount_info = failed_payment.get("amount") or {}

    event_type = event.get("event_type", "")

    # Extract subscription ID
    subscription_id = (
        resource.get("id")
        if event_type.startswith("BILLING.SUBSCRIPTION.")
        else resource.get("billing_agreement_id")
        or resource.get("subscription_id")
    )

    # Extract payment information
    failure_reason = failed_payment.get("reason_code")
    amount = amount_info.get("value")
    currency = amount_info.get("currency_code")
    failed_count = billing_info.get("failed_payments_count")
    next_retry = failed_payment.get("next_payment_retry_date")
    print("\n===== DEBUG PAYMENT DATA =====")
    print("\n===== DEBUG PAYMENT DATA =====")
    print("Subscription ID:", subscription_id)
    print("Failure Reason:", failure_reason)
    print("Amount:", amount)
    print("Currency:", currency)
    print("Failed Count:", failed_count)
    print("Next Retry:", next_retry)
    print("=============================\n")     

    prompt = f"""
You are RecoverAI, a payment recovery assistant for business owners.

Explain this failed payment in simple language.

Event ID: {event.get("id")}
Event Type: {event_type}

Extracted Payment Details:
Subscription ID: {subscription_id or "Not available"}
Failure Reason: {failure_reason or "Not available"}
Failed Amount: {amount or "Not available"}
Currency: {currency or "Not available"}
Failed Payment Count: {failed_count if failed_count is not None else "Not available"}
Next Retry Date: {next_retry or "Not available"}

Provide a concise report with exactly these five sections:

1. Event Summary
Explain in one simple sentence what happened.

2. Subscription Details
Show the subscription ID if available.
Do not confuse a failed payment attempt with a cancelled subscription.

3. Relevant Payment Information
Show failure reason, amount, currency, failed payment count,
and next retry date wherever available.
Never invent missing information.

4. Recommended Action
Give 1-2 specific steps the business owner should take next.

5. A Professional Customer Recovery Message
Write a short, polite message ready to copy and send.

Important:
- Use the extracted details above.
- Keep the report concise and easy to scan.
- Use simple language.
- Never invent missing information.
- Never claim payment has been recovered unless PayPal confirms it.
- Never claim a retry has happened unless confirmed.
"""

    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return response.text



def save_ai_recommendation(event_id, recommendation):

    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO ai_recommendations
            (event_id, recommendation)
            VALUES (?, ?)
            ON CONFLICT(event_id)
            DO UPDATE SET
                recommendation = excluded.recommendation,
                created_at = CURRENT_TIMESTAMP
        """, (event_id, recommendation))

        conn.commit()
        print("AI recommendation saved successfully!")

    finally:
        conn.close()



# Initialize database on startup.
initialize_database()


# ---------------- PAYPAL WEBHOOK ----------------

@app.post("/paypal-webhook")
async def paypal_webhook(request: Request):

    raw_body = await request.body()

    try:
        event = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON event"
        )

    print("\nPayPal Webhook Received!")
    print("Event Type:", event.get("event_type"))

    headers = request.headers

    try:

        if not all([
            headers.get("paypal-auth-algo"),
            headers.get("paypal-cert-url"),
            headers.get("paypal-transmission-id"),
            headers.get("paypal-transmission-sig"),
            headers.get("paypal-transmission-time")
        ]):
            raise HTTPException(
                status_code=400,
                detail="Missing PayPal signature headers"
            )

        # Simulator verification.
        is_valid = verify_local_signature(
            headers,
            raw_body,
            SIMULATOR_WEBHOOK_ID
        )

        if is_valid:

            print("Simulator Signature Verified!")

        else:

            # Official PayPal verification.
            if not REAL_WEBHOOK_ID:
                raise HTTPException(
                    status_code=401,
                    detail="Signature verification failed"
                )

            is_valid = verify_real_paypal_event(
                headers,
                event
            )

            if not is_valid:
                raise HTTPException(
                    status_code=401,
                    detail="PayPal signature verification failed"
                )

            print("Real PayPal Signature Verified!")

    except HTTPException:
        raise

    except Exception as error:

        print("Verification Error:", error)

        raise HTTPException(
            status_code=500,
            detail="Webhook verification could not be completed"
        )

    event_type = event.get("event_type")

    if event_type == "BILLING.SUBSCRIPTION.PAYMENT.FAILED":
        print("Alert: Subscription payment failed!")

    elif event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        print("Subscription Activated!")

    elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        print("Subscription Cancelled!")

    elif event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
        print("Subscription Suspended!")

    # Save event.
    try:

        is_new_event = save_event(event)

    except Exception as error:

        print("Database Error:", error)

        raise HTTPException(
            status_code=500,
            detail="Could not save webhook event"
        )

    # Analyze only new failed-payment events.
    ai_triggered = False

    if (
        is_new_event
        and event_type == "BILLING.SUBSCRIPTION.PAYMENT.FAILED"
    ):

        ai_triggered = True

        print("\nRecoverAI: Starting Gemini analysis...")

        try:

            recommendation = analyze_failed_payment(event)

            save_ai_recommendation(
                event.get("id"),
                recommendation
            )

            print("\n===== RECOVERAI AI ANALYSIS =====")
            print(recommendation)

        except Exception as error:

            print("Gemini Analysis Error:", error)

    return {
        "status": "success",
        "event_saved": is_new_event,
        "ai_analysis_triggered": ai_triggered
    }


# ---------------- FRONTEND DASHBOARD API ----------------


@app.get("/dashboard-data")
def dashboard_data():

    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*) FROM webhook_events
        """)
        total_events = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM webhook_events
            WHERE event_type = 'BILLING.SUBSCRIPTION.PAYMENT.FAILED'
        """)
        failed_payments = cursor.fetchone()[0]

        cursor.execute("""
    SELECT
        COALESCE(recovery_status, 'Pending'),
        COUNT(*)
    FROM webhook_events
    WHERE event_type = 'BILLING.SUBSCRIPTION.PAYMENT.FAILED'
    GROUP BY COALESCE(recovery_status, 'Pending')
""")

        status_rows = cursor.fetchall()

        recovery_summary = {
    "Pending": 0,
    "Contacted": 0,
    "Recovered": 0,
    "Unresolved": 0
}

        for status, count in status_rows:
         if status in recovery_summary:
           recovery_summary[status] = count

        

        cursor.execute("""
            SELECT COUNT(*) FROM ai_recommendations
        """)
        ai_analyses = cursor.fetchone()[0]

        cursor.execute("""
            SELECT event_id, subscription_id, event_type, created_at, recovery_status
            FROM webhook_events
            WHERE event_type = 'BILLING.SUBSCRIPTION.PAYMENT.FAILED'
            ORDER BY id DESC
            LIMIT 10
        """)

        rows = cursor.fetchall()

        recent_payments = [
            {
                "event_id": row[0],
                "subscription_id": row[1],
                "event_type": row[2],
                "created_at": row[3],
                "recovery_status": row[4] or "Pending"
            }
            for row in rows
        ]

        cursor.execute("""
            SELECT recommendation
            FROM ai_recommendations
            ORDER BY created_at DESC
            LIMIT 1
        """)

        result = cursor.fetchone()
        latest_analysis = result[0] if result else None

        # Fetch latest 8 webhook events for activity timeline
        cursor.execute("""
            SELECT event_type, subscription_id, created_at
            FROM webhook_events
            ORDER BY id DESC
            LIMIT 8
        """)

        activity_rows = cursor.fetchall()

        recent_activity = [
            {
                "event_type": row[0],
                "subscription_id": row[1],
                "created_at": row[2]
            }
            for row in activity_rows
        ]

        return {
            "total_events": total_events,
            "failed_payments": failed_payments,
            "ai_analyses": ai_analyses,
            "recent_payments": recent_payments,
            "latest_analysis": latest_analysis,
            "recent_activity": recent_activity,
            "recovery_summary": recovery_summary
        }

    finally:
        conn.close()





class RecoveryStatusUpdate(BaseModel):
    status: str

class ChatRequest(BaseModel):
    message: str


@app.patch("/recovery-status/{event_id}")
async def update_recovery_status(
    event_id: str,
    data: RecoveryStatusUpdate
):

    new_status = data.status

    allowed_statuses = [
        "Pending",
        "Contacted",
        "Recovered",
        "Unresolved"
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid recovery status"
        )

    if new_status == "Recovered":
        raise HTTPException(
            status_code=400,
            detail="Recovery requires confirmed PayPal payment success."
        )

    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT event_id
            FROM webhook_events
            WHERE event_id = ?
        """, (event_id,))

        event = cursor.fetchone()

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        cursor.execute("""
            UPDATE webhook_events
            SET recovery_status = ?,
                contacted_at = CASE
                    WHEN ? = 'Contacted'
                    THEN CURRENT_TIMESTAMP
                    ELSE contacted_at
                END
            WHERE event_id = ?
        """, (new_status, new_status, event_id))

        conn.commit()

        return {
            "message": "Recovery status updated successfully",
            "event_id": event_id,
            "status": new_status
        }

    finally:
        conn.close()


# ---------------- MANUAL AI ANALYSIS API ----------------

@app.post("/analyze-payment/{event_id}")
def manually_analyze_payment(event_id: str):

    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT event_id, event_type, resource_json
            FROM webhook_events
            WHERE event_id = ?
        """, (event_id,))

        row = cursor.fetchone()

    finally:
        conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Payment event not found"
        )

    if row[1] != "BILLING.SUBSCRIPTION.PAYMENT.FAILED":
        raise HTTPException(
            status_code=400,
            detail="AI analysis is only available for failed subscription payments."
        )

    try:
        event = {
            "id": row[0],
            "event_type": row[1],
            "resource": json.loads(row[2] or "{}")
        }
        print("\n===== STORED RESOURCE JSON =====")
        print(json.dumps(event["resource"], indent=2))
        print("================================\n")

        print("Manual Gemini analysis started:", event_id)

        recommendation = analyze_failed_payment(event)

        save_ai_recommendation(
            event_id,
            recommendation
        )

        return {
            "status": "success",
            "event_id": event_id,
            "recommendation": recommendation
        }

    except Exception as error:
        print("Manual AI Analysis Error:", error)

        raise HTTPException(
            status_code=500,
            detail="Could not generate AI recommendation."
        )
# ---------------- AI CHAT ASSISTANT API ----------------

@app.post("/chat")
def chat_with_recoverai(data: ChatRequest):

    if not gemini_client:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing in .env"
        )

    message = data.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Please enter a message."
        )

    if len(message) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Message is too long. Maximum 1000 characters."
        )

    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                w.event_id,
                w.event_type,
                w.subscription_id,
                w.created_at,
                w.recovery_status,
                w.resource_json,
                (
                    SELECT a.recommendation
                    FROM ai_recommendations a
                    WHERE a.event_id = w.event_id
                    ORDER BY a.created_at DESC
                    LIMIT 1
                )
            FROM webhook_events w
            ORDER BY w.id DESC
            LIMIT 15
        """)

        rows = cursor.fetchall()

    finally:
        conn.close()

    payment_records = []

    for row in rows:

        resource = json.loads(row[5] or "{}")

        billing_info = resource.get("billing_info") or {}
        failed_payment = billing_info.get("last_failed_payment") or {}
        amount_info = failed_payment.get("amount") or {}

        payment_records.append({
            "event_id": row[0],
            "event_type": row[1],
            "subscription_id": row[2],
            "created_at": row[3],
            "recovery_status": row[4] or "Pending",
            "amount": amount_info.get("value"),
            "currency": amount_info.get("currency_code"),
            "failure_reason": failed_payment.get("reason_code"),
            "failed_payment_count": billing_info.get("failed_payments_count"),
            "ai_recommendation": row[6]
        })

    prompt = f"""
You are RecoverAI, an AI chat assistant for subscription businesses.

The business owner is asking:
{message}

Here is the latest payment and subscription data stored in the RecoverAI database:
{json.dumps(payment_records, indent=2)}

Instructions:
1. Answer using only the database information provided.
2. Never invent customer names, emails, amounts, dates, or payment details.
3. If information is unavailable, clearly say it is not available in the records.
4. Explain payment failures and AI recommendations in simple language.
5. Do not claim a payment was recovered unless its recovery status is Recovered.
6. Do not claim that a retry or customer message was sent.
7. Give clear, concise and helpful answers.
8. If there are no relevant records, say so honestly.
"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return {
            "reply": response.text
        }

    except Exception as error:
        print("RecoverAI Chat Error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to generate a response. Please try again."
        )
# ---------------- SUBSCRIPTION APPROVAL ----------------

@app.get("/success")
def subscription_success():
    return RedirectResponse(
        url="http://127.0.0.1:5500/index.html?subscription=approved"
    )


@app.get("/cancel")
def subscription_cancel():
    return RedirectResponse(
        url="http://127.0.0.1:5500/index.html?subscription=cancelled"
    )
