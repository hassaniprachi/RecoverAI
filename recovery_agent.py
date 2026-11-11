
import os
import json
import sqlite3
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def get_events():

    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT event_id, event_type, subscription_id, resource_json
        FROM webhook_events
        ORDER BY id DESC
    """)

    events = cursor.fetchall()
    conn.close()

    return events


def analyze_event(event):

    event_id, event_type, subscription_id, resource_json = event

    resource = json.loads(resource_json) if resource_json else {}

    prompt = f"""
    You are RecoverAI, an intelligent PayPal subscription assistant.

    Analyze this PayPal webhook event:

    Event ID: {event_id}
    Event Type: {event_type}
    Subscription ID: {subscription_id}

    PayPal Resource Details:
    {json.dumps(resource, indent=2)}

    Give the following output:

    1. Event summary.
    2. Subscription status, if available.
    3. Relevant payment information, if available.
    4. Recommended next action.
    5. A professional customer message, if action is needed.

    Important:
    - Never invent missing payment information.
    - If this is a reactivated event, explain that the subscription is active again.
    - Do not claim that a payment was recovered unless the event confirms it.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text



if __name__ == "__main__":

    events = get_events()

    if not events:
        print("No webhook events found.")

    else:
        for event in events:

            if event[1] != "BILLING.SUBSCRIPTION.PAYMENT.FAILED":
                continue

            print("\n===== RECOVERAI AI ANALYSIS =====")
            print("Event Type:", event[1])

            try:
                analysis = analyze_event(event)

                print(analysis)

                conn = sqlite3.connect("recoverai.db")
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR IGNORE INTO ai_recommendations
                    (event_id, recommendation)
                    VALUES (?, ?)
                """, (event[0], analysis))

                conn.commit()
                conn.close()

                print("\nAI recommendation saved to database!")

            except Exception as error:
                print("AI Analysis Error:", error)
