# 🛡️ Sentinela

> A real-time, automated personal finance tracker that intercepts Apple Pay transactions and syncs them to a PostgreSQL cloud database with instant Telegram categorization.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

## 📖 Overview

Sentinela is a completely frictionless expense tracker designed to bypass the limitations of manual budgeting apps. By utilizing an iOS Shortcut automation, it silently intercepts Apple Pay taps at the OS level and forwards the transaction data to a secure FastAPI backend. 

Instead of opening a budgeting app, Sentinela immediately sends a **Push Notification via Telegram**. The user categorizes the transaction directly from the Telegram notification using interactive inline buttons, updating the cloud database in real-time.

## ✨ Features

- **Zero-Friction Logging:** Intercepts Apple Pay transactions instantly via iOS Shortcuts.
- **Interactive Telegram UI:** Categorize transactions from your lock screen without opening an app.
- **Dynamic Daily Budgeting:** Automatically calculates a strict daily spend limit based on your disposable income and remaining days in the month.
- **iOS Home Screen Widget:** Includes a custom `Scriptable` JavaScript widget for a beautiful, real-time budget dashboard on your iPhone.
- **Cloud Native:** Dockerized and fully ready for deployment on Render, Fly.io, or AWS with a PostgreSQL (Supabase) database.

## 🏗️ System Architecture

1. **Trigger (iOS):** User taps their card via Apple Pay. An iOS Shortcut Personal Automation detects the transaction and extracts the Merchant, Amount, and Currency.
2. **Ingestion (FastAPI):** A `POST` request is sent to the `/api/v1/transactions/webhook` endpoint. Pydantic validates the payload and verifies the API Key.
3. **Storage (PostgreSQL):** SQLAlchemy commits the transaction to the database with a default "Uncategorized" tag.
4. **Notification (Telegram):** A FastAPI Background Task triggers the Telegram Bot API to send a rich message with inline category buttons.
5. **Categorization (Webhook):** When the user taps a button, Telegram fires a webhook back to Sentinela. The backend updates the database category, recalculates the daily budget, and edits the Telegram message to show a success checkmark and the remaining daily budget.

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Data & ORM:** SQLAlchemy, Pydantic, PostgreSQL
- **Integrations:** Telegram Bot API
- **Deployment:** Docker, Render, Supabase

## 🚀 Getting Started

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/Krishna-Suri-7/Sentinela.git
cd Sentinela
```

2. **Set up the virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Environment Variables**
Create a `.env` file in the root directory:
```env
API_KEY="your_secure_api_key"
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
TELEGRAM_CHAT_ID="your_telegram_chat_id"
DATABASE_URL="sqlite:///./data/sentinela.db" # Or your Postgres URL
MONTHLY_INCOME="3000"
FIXED_EXPENSES="1200"
SAVINGS_GOAL="500"
```

4. **Run the Server**
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

## 🧪 Testing

This project uses `pytest` for unit testing the API and database logic.
```bash
pytest tests/
```
