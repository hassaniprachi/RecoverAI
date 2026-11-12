# RecoverAI ✨
### AI-Powered Failed Payment Recovery Assistant

RecoverAI is an AI-powered subscription payment monitoring and recovery assistant built using the PayPal Developer Sandbox and Google Gemini.

It helps subscription businesses monitor subscription payment events, understand payment failures, view AI-generated recovery insights, and interact with an AI assistant to get recommendations for handling payment issues.

## 🚀 Problem Statement

Subscription businesses lose revenue when recurring payments fail due to expired cards, insufficient funds, or payment declines.

Understanding these failures and deciding what action to take can be time-consuming.

RecoverAI aims to simplify failed-payment monitoring and recovery insights through PayPal webhook integration and AI-powered assistance.

## 💡 Key Features

- **PayPal Integration:** Integrates with the PayPal Developer Sandbox and Subscriptions API.
- **Webhook Monitoring:** Receives and processes subscription-related PayPal webhook events.
- **Payment Failure Detection:** Identifies failed subscription payment events.
- **AI Recovery Insights:** Uses Google Gemini to generate contextual recovery recommendations.
- **AI Chat Assistant:** Allows users to ask questions about payment failures, subscription events, and recovery insights.
- **Dashboard:** Displays subscription and payment information through a web interface.
- **Event Storage:** Stores webhook event information using SQLite.

## 🛠️ Tools and Technologies Used

| Technology / Tool | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | Backend API and webhook server |
| PayPal Developer Sandbox | Subscription and payment integration |
| PayPal Subscriptions API | Subscription management |
| PayPal Webhooks | Receives subscription-related event notifications |
| Google Gemini (`gemini-2.5-flash`) | AI-powered insights and chat responses |
| SQLite | Stores webhook events and application data |
| HTML, CSS, JavaScript | Frontend dashboard and chat interface |
| Ngrok | Exposes the local webhook endpoint during testing |
| GitHub | Source code hosting and version control |

## 🏗️ Project Architecture

1. PayPal generates subscription-related events.
2. PayPal sends webhook notifications to the RecoverAI backend.
3. FastAPI receives and processes the webhook events.
4. Event information is stored in an SQLite database.
5. Google Gemini uses available payment-event information and the user's question to generate contextual responses.
6. The frontend dashboard displays subscription information and provides an interactive AI chat assistant.

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
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites

- Python 3 installed
- Git installed
- Visual Studio Code
- VS Code Live Server extension
- PayPal Developer Sandbox account
- Google Gemini API key

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

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root directory.

Use `.env.example` as a template and add your own credentials:

```env
Client_id=YOUR_PAYPAL_CLIENT_ID
Secret_id=YOUR_PAYPAL_SECRET
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_WEBHOOK_ID=YOUR_PAYPAL_WEBHOOK_ID
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

You must provide your own PayPal Sandbox credentials and Gemini API key.

**Important:** Never upload your actual `.env` file, API keys, client secrets, or access tokens to GitHub.

### 5. Start the backend

Run:

```bash
uvicorn webhook:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at:

`http://127.0.0.1:8000`

FastAPI interactive API documentation:

`http://127.0.0.1:8000/docs`

Keep the backend terminal running.

### 6. Start the frontend

1. Open the RecoverAI project folder in Visual Studio Code.
2. Open `index.html`.
3. Right-click the file.
4. Select **Open with Live Server**.
5. The RecoverAI dashboard will open in your browser.

### 7. Configure PayPal webhooks

1. Open the PayPal Developer Dashboard.
2. Select your Sandbox application.
3. Configure a webhook using your publicly accessible backend URL.
4. Select the required subscription and payment event types.
5. For local development, use Ngrok to expose your FastAPI server.

Example Ngrok command:

```bash
ngrok http 8000
```

Use the generated HTTPS forwarding URL when configuring your PayPal webhook, with the appropriate webhook endpoint path.

## 🧪 Testing

The project supports testing of:

- PayPal Sandbox authentication.
- Product and subscription setup.
- Subscription webhook event reception.
- Payment failure event processing.
- Webhook event storage in SQLite.
- AI chat responses based on stored application data.
- AI-generated recovery recommendations.

PayPal Sandbox webhook events and test events can be used to demonstrate webhook processing.

## 🔮 Future Improvements

- Automated payment retry scheduling.
- Personalized customer recovery notifications.
- Advanced recovery analytics.
- Production PayPal integration.
- Improved subscription recovery tracking.

## ⚠️ Current Project Scope

RecoverAI currently focuses on webhook-based subscription event monitoring, payment failure identification, AI-generated recovery insights, and an interactive AI chat assistant.

The AI assistant provides recommendations based on available application data.

Automated payment retries and customer notifications are future improvements and are not currently implemented.

The project uses the PayPal Developer Sandbox for demonstration and testing purposes.

## 👩‍💻 Project Repository

**GitHub:** https://github.com/hassaniprachi/RecoverAI

**License:** MIT License

---

**RecoverAI — Making Subscription Payment Recovery Smarter with AI.**