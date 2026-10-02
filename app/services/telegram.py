import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
TELEGRAM_EDIT_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"


def build_category_keyboard(prefix: str, categories: list) -> dict:
    keyboard = []
    row = []
    for cat in categories:
        btn_text = f"{cat['emoji']} {cat['name']}"
        # using cat name as callback data, keep it short
        btn_data = f"{prefix}_{cat['name']}"
        row.append({"text": btn_text, "callback_data": btn_data})
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return {"inline_keyboard": keyboard}

async def send_transaction_notification(merchant: str, amount: float, currency: str = "EUR", tx_id: int = None, categories: list = None) -> bool:
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
    
    # If no categories passed, fallback
    if not categories:
        categories = [{"name": "Other", "emoji": "📦"}]
        
    inline_keyboard = build_category_keyboard(prefix, categories)

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

async def edit_message_to_confirmed(chat_id: int, message_id: int, merchant: str, amount: float, currency: str, category: str, remaining_budget: float = None, categories: list = None, tx_id: int = None) -> bool:
    if not TELEGRAM_BOT_TOKEN:
        return False
        
    # Find emoji for the chosen category
    cat_emoji = "✅"
    if categories:
        for cat in categories:
            if cat["name"] == category:
                cat_emoji = cat["emoji"]
                break
                
    cat_label = f"{cat_emoji} {category}"
    
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

    # Re-attach keyboard so they can edit it later
    inline_keyboard = None
    if categories and tx_id:
        inline_keyboard = build_category_keyboard(f"tx_{tx_id}", categories)

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": message_text,
        "parse_mode": "Markdown",
    }
    
    if inline_keyboard:
        payload["reply_markup"] = inline_keyboard
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
