import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
# Filters-কে এখন telegram.ext.filters মডিউল থেকে আমদানি করা হচ্ছে
from telegram.ext import filters 
import requests
import json
import os

# --- কনফিগারেশন: এই ভ্যালুগুলো Render Environment Variables থেকে স্বয়ংক্রিয়ভাবে নেওয়া হবে ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") 
PROXY_URL = os.environ.get("RENDER_PROXY_URL")
# ------------------

def start(update, context):
    """বট শুরু করার কমান্ড (/start) হ্যান্ডেল করে।"""
    update.message.reply_text("স্বাগতম! Free Fire-এর লাইক রিকোয়েস্ট পাঠাতে আপনার UID দিন।")

def send_like_request(uid):
    """আপনার প্রক্সি সার্ভারকে কল করে লাইক রিকোয়েস্ট পাঠায়।"""
    if not PROXY_URL:
        return "❌ এরর: প্রক্সি URL সেট করা নেই। Render কনফিগারেশন চেক করুন।"

    try:
        payload = {"id": uid}
        
        # আপনার হোস্টেড প্রক্সি সার্ভারে POST রিকোয়েস্ট পাঠানো হচ্ছে
        response = requests.post(PROXY_URL, json=payload, timeout=15)
        response.raise_for_status() # HTTP এরর হলে এক্সেপশন থ্রো করবে
        
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
        print(f"Proxy Request Error: {e}")
        return "❌ সংযোগ এরর। প্রক্সি সার্ভার (Render) বর্তমানে নিষ্ক্রিয় (Idle) থাকতে পারে বা URL ভুল। পরে চেষ্টা করুন।"

def handle_message(update, context):
    """ব্যবহারকারীর পাঠানো UID মেসেজটি হ্যান্ডেল করে।"""
    user_input = update.message.text.strip()
    
    # ইনপুট যাচাই
    if user_input.isdigit() and len(user_input) >= 8 and len(user_input) <= 15:
        update.message.reply_text(f"UID ({user_input}) গৃহীত হয়েছে। লাইক রিকোয়েস্ট পাঠানো হচ্ছে...")
        
        # মূল প্রক্সি ফাংশন কল করা
        response_message = send_like_request(user_input)
        
        update.message.reply_text(response_message)
    else:
        update.message.reply_text("দয়া করে একটি সঠিক Free Fire UID (শুধুমাত্র সংখ্যা) লিখুন।")


def main():
    if not TELEGRAM_BOT_TOKEN:
        print("FATAL ERROR: TELEGRAM_BOT_TOKEN is not set.")
        return

    # Updater শুরু করা
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command Handler
    dp.add_handler(CommandHandler("start", start))
    
    # Message Handler (Filters.text এর পরিবর্তে filters.TEXT ব্যবহার করা হলো)
    # filters.COMMAND বাদ দিয়ে শুধু টেক্সট মেসেজ হ্যান্ডেল করা হচ্ছে
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # বট শুরু: Long Polling মোড ব্যবহার করা হচ্ছে
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
