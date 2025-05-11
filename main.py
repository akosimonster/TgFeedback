import telebot
import time
import traceback
import os
from dotenv import load_dotenv

# Load token from .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Configuration
TARGET_USER_ID = 6025939560
OWNER_ID = 6025939560
blocked_users = set()
forwarded_map = {}

@bot.message_handler(commands=['block'])
def block_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return
    try:
        user_id = int(message.text.split()[1])
        blocked_users.add(user_id)
        bot.reply_to(message, f"✅ User {user_id} has been blocked.")
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Usage: /block <user_id>")

@bot.message_handler(commands=['unblock'])
def unblock_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return
    try:
        user_id = int(message.text.split()[1])
        blocked_users.discard(user_id)
        bot.reply_to(message, f"✅ User {user_id} has been unblocked.")
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Usage: /unblock <user_id>")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "🤖 *This bot is made by Fritz!*\n\n"
        "📜 *Rules:*\n"
        "1️⃣ *Do not send any sensitive videos such as pornography or gore.*\n"
        "2️⃣ *Only send content related to Call of Duty: Mobile (CODM).* \n"
        "3️⃣ *Failure to follow these rules will result in being blocked from this bot!*\n\n"
        "✅ *By using this bot, you agree to follow these rules.*",
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['text', 'photo', 'document', 'video', 'audio', 'sticker'])
def forward_message(message):
    user_id = message.from_user.id
    if user_id in blocked_users:
        bot.send_message(message.chat.id, "🚫 You have been blocked from using this bot.")
        return

    first_name = message.from_user.first_name or "Unknown"
    username = message.from_user.username or "No Username"
    print(f"Message from {first_name} (@{username} | ID: {user_id})")

    temp_msg = bot.send_message(message.chat.id, "📨 Your message is being forwarded to Fritz...")
    time.sleep(1.5)
    bot.delete_message(message.chat.id, temp_msg.message_id)

    fwd_msg = bot.forward_message(TARGET_USER_ID, message.chat.id, message.message_id)
    forwarded_map[fwd_msg.message_id] = user_id

@bot.message_handler(func=lambda message: message.reply_to_message is not None and message.from_user.id == OWNER_ID)
def reply_handler(message):
    replied_msg_id = message.reply_to_message.message_id
    if replied_msg_id in forwarded_map:
        original_user_id = forwarded_map[replied_msg_id]
        bot.send_message(original_user_id, f"📩 *Reply from Fritz:*\n\n{message.text}", parse_mode="Markdown")

print("🤖 Bot is running and forwarding messages...")

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("❌ Bot crashed. Restarting in 5 seconds...")
        traceback.print_exc()
        time.sleep(5)
