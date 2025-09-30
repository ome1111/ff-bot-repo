# WARNING: This is a fallback code using an older structure to bypass Render conflicts.

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import requests
import json
import os
import time 

# --- কনফিগারেশন ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") 
PROXY_URL = os.environ.get("RENDER_PROXY_URL")
# ------------------

def start(update, context):
    update.message.reply_text("স্বাগতম! Free Fire-এর লাইক রিকোয়েস্ট পাঠাতে আপনার UID দিন।")

def send_like_request(uid):
    # (HTTP request logic remains the same)
    if not PROXY_URL:
        return "❌ এরর: প্রক্সি URL সেট করা নেই। Render কনফিগারেশন চেক করুন।"

    try:
        payload = {"id": uid}
        response = requests.post(PROXY_URL, json=payload, timeout=15)
        response.raise_for_status() 
        result = response.json()

        if result.get("status") == "success":
            sent_likes = result.get("api", {}).get("BotSend", 0)
            if sent_likes > 0:
                return f"✅ সফল! **{sent_likes}** টি লাইক রিকোয়েস্ট পাঠানো হয়েছে। একদিন পর আবার চেষ্টা করুন।"
            else:
                return "❌ ব্যর্থ: আজকের সীমা অতিক্রম হয়েছে বা Free Fire Mania সার্ভারে কোনো এরর হয়েছে। আবার চেষ্টা করুন।"
        else:
            return f"❌ এরর: প্রক্সি সার্ভার থেকে এরর এসেছে। মেসেজ: {result.get('message', 'অজানা এরর')}"

    except requests.exceptions.RequestException as e:
        return "❌ সংযোগ এরর। প্রক্সি সার্ভার (Render) বর্তমানে নিষ্ক্রিয় (Idle) থাকতে পারে বা URL ভুল। পরে চেষ্টা করুন।"

def handle_message(update, context):
    user_input = update.message.text.strip()
    
    if user_input.isdigit() and len(user_input) >= 8 and len(user_input) <= 15:
        # এখানে কোনো await ব্যবহার করা যাবে না, কারণ এটি পুরোনো Updater স্ট্রাকচার
        update.message.reply_text(f"UID ({user_input}) গৃহীত হয়েছে। লাইক রিকোয়েস্ট পাঠানো হচ্ছে...")
        
        response_message = send_like_request(user_input)
        
        update.message.reply_text(response_message)
    else:
        update.message.reply_text("দয়া করে একটি সঠিক Free Fire UID (শুধুমাত্র সংখ্যা) লিখুন।")


def main():
    if not TELEGRAM_BOT_TOKEN:
        print("FATAL ERROR: TELEGRAM_BOT_TOKEN is not set.")
        return

    # Old Updater Structure (Simplified for compatibility)
    # WARNING: The 'use_context=True' or lack thereof can be an issue.
    # We remove it and hope Render's old Python version supports this.
    try:
        updater = Updater(TELEGRAM_BOT_TOKEN) 
    except Exception as e:
        print(f"Updater Initialization Failed: {e}")
        time.sleep(10) # Give time for the system to crash gracefully
        return


    dp = updater.dispatcher

    # Handlers যোগ করা
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # বট শুরু: Long Polling মোড
    print("Telegram Bot Long Polling শুরু হচ্ছে...")
    updater.start_polling() 
    updater.idle()

if __name__ == '__main__':
    main()
