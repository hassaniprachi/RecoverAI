# RecoverAI ✨
### AI-Powered Failed Payment Recovery Assistant

RecoverAI is an AI-powered subscription payment monitoring and recovery assistant built using the PayPal Developer Sandbox and Google Gemini.

It helps subscription businesses understand failed payment events, view recovery insights, and interact with an AI assistant to get recommendations for handling payment failures.

## 🚀 Problem Statement

Subscription businesses lose revenue when recurring payments fail due to expired cards, insufficient funds, or payment declines.

RecoverAI aims to make failed-payment monitoring and recovery insights easier through webhook-based event tracking and AI-powered assistance.

## 💡 Key Features

- **PayPal Integration:** Integrates with the PayPal Sandbox and Subscriptions API.
- **Webhook Monitoring:** Receives and processes subscription-related PayPal webhook events.
- **Payment Failure Detection:** Identifies failed subscription payment events.
- **AI Recovery Insights:** Uses Google Gemini to generate recovery recommendations.
- **AI Chat Assistant:** Allows users to ask questions about payment failures, subscription events, and recovery insights.
- **Dashboard:** Displays payment and subscription information through a web interface.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | API and webhook server |
| PayPal Developer Sandbox | Payment and subscription integration |
| Google Gemini | AI-powered assistant |
| SQLite | Event and application data storage |
| HTML, CSS, JavaScript | Frontend dashboard |
| Ngrok | Exposing local webhook endpoint during testing |

## 🏗️ Project Architecture

1. PayPal generates subscription-related events.
2. PayPal sends webhook notifications to the RecoverAI backend.
3. FastAPI receives and processes the events.
4. Event information is stored in SQLite.
5. Gemini uses available event data and the user's question to generate contextual responses.
6. The frontend dashboard displays information and provides an AI chat interface.

## 📂 Project Structure

```text
RecoverAI/
│
├── index.html
├── webhook.py
├── database.py
├── recovery_agent.py
├── paypal_auth.py
├── paypal_product.py
├── paypal_plan.py
├── paypal_subscription.py
├── check_plan.py
├── check_subs.py
├── checknew_sub.py
├── list_subs.py
├── gemini_test.py
├── list_models.py
├── view_ai.py
├── view_database.py
├── product_info.txt
├── .gitignore
└── README.md
```

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/hassaniprachi/RecoverAI.git
cd RecoverAI
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

Install the Python packages required by the backend and AI integration.

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
Client_id=YOUR_PAYPAL_CLIENT_ID
Secret_id=YOUR_PAYPAL_SECRET
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_WEBHOOK_ID=YOUR_PAYPAL_WEBHOOK_ID
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Never commit your `.env` file or expose API credentials.

### 5. Start the backend

```bash
uvicorn webhook:app --host 127.0.0.1 --port 8000 --reload
```

Backend API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the frontend

Open `index.html` using VS Code Live Server.

### 7. Configure PayPal webhooks

Configure your PayPal Sandbox webhook to point to your publicly accessible backend webhook URL.

Use Ngrok during local development to expose the backend.

## 🧪 Testing

The project supports testing of:
- PayPal Sandbox authentication
- Product and subscription setup
- Subscription webhook event reception
- Payment failure event processing
- AI chat responses based on stored application data

## 🔮 Future Improvements

- Automated payment retry scheduling
- Personalized customer recovery notifications
- Advanced recovery analytics
- Production PayPal integration
- Improved subscription recovery tracking

## ⚠️ Current Scope

RecoverAI currently focuses on webhook-based event monitoring, AI-generated recovery insights, and an interactive AI chat assistant.

Automated payment retries and customer notifications are future improvements, not currently implemented features.

## 👩‍💻 Project Repository

[GitHub – RecoverAI](https://github.com/hassaniprachi/RecoverAI)

---

**RecoverAI — Making Subscription Payment Recovery Smarter with AI.**