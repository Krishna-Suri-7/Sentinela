import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
TELEGRAM_EDIT_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"


async def send_transaction_notification(merchant: str, amount: float, currency: str = "EUR", tx_id: int = None) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram Service] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID.")
        return False

    message_text = (
        f"💳 *Sentinela: Payment Detected*\n\n"
        f"🏪 *Merchant:* `{merchant}`\n"
        f"💰 *Amount:* `{amount:.2f} {currency}`\n\n"
        f"Tap a button to categorize:"
    )

    prefix = f"tx_{tx_id}" if tx_id else "tx_new"
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "🛒 Groceries", "callback_data": f"{prefix}_groceries"},
                {"text": "🍔 Dining", "callback_data": f"{prefix}_dining"},
            ],
            [
                {"text": "🚌 Transport", "callback_data": f"{prefix}_transport"},
                {"text": "🛍️ Shopping", "callback_data": f"{prefix}_shopping"},
            ],
            [
                {"text": "💡 Bills / Sub", "callback_data": f"{prefix}_bills"},
                {"text": "📦 Other", "callback_data": f"{prefix}_other"},
            ],
        ]
    }

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown",
        "reply_markup": inline_keyboard,
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            response = await client.post(TELEGRAM_API_URL, json=payload)
            response.raise_for_status()
            return True
        except Exception as err:
            print(f"[Telegram Service] Failed to send alert: {err}")
            return False

async def edit_message_to_confirmed(chat_id: int, message_id: int, merchant: str, amount: float, currency: str, category: str, remaining_budget: float = None) -> bool:
    if not TELEGRAM_BOT_TOKEN:
        return False
        
    emoji_map = {
        "groceries": "🛒 Groceries",
        "dining": "🍔 Dining",
        "transport": "🚌 Transport",
        "shopping": "🛍️ Shopping",
        "bills": "💡 Bills / Sub",
        "other": "📦 Other",
    }
    
    cat_label = emoji_map.get(category, category.capitalize())
    
    message_text = (
        f"💳 *Sentinela: Payment Logged*\n\n"
        f"🏪 *Merchant:* `{merchant}`\n"
        f"💰 *Amount:* `{amount:.2f} {currency}`\n"
        f"✅ *Category:* {cat_label}"
    )
    
    if remaining_budget is not None:
        if remaining_budget >= 0:
            message_text += f"\n\n📊 *Remaining Today:* `{remaining_budget:.2f} {currency}`"
        else:
            message_text += f"\n\n⚠️ *Over Budget Today:* `{abs(remaining_budget):.2f} {currency}`"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    # No reply_markup so it removes the buttons

    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            response = await client.post(TELEGRAM_EDIT_API_URL, json=payload)
            response.raise_for_status()
            return True
        except Exception as err:
            print(f"[Telegram Service] Failed to edit message: {err}")
            return False

async def answer_callback_query(callback_query_id: str):
    if not TELEGRAM_BOT_TOKEN:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            await client.post(url, json=payload)
            return True
        except Exception as err:
            print(f"[Telegram Service] Failed to answer callback query: {err}")
            return False
