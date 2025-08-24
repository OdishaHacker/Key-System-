from telegram.ext import Updater, CommandHandler
from flask import Flask, request, jsonify
import os, random, string, datetime, atexit, signal, sys, threading

# Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1973297878

# Memory storage
user_keys = {}
active_users = set()

# Flask app
app = Flask(__name__)

def generate_key():
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"ODISHA-HACKER-24H-{random_part}"

def check_and_get_key(user_id):
    now = datetime.datetime.utcnow()
    if user_id in user_keys:
        expire_time = datetime.datetime.strptime(user_keys[user_id]["expire_time"], "%Y-%m-%d %H:%M:%S")
        if expire_time > now:
            return user_keys[user_id]   # still valid
    # new key
    expire_time = (now + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    user_keys[user_id] = {
        "key": generate_key(),
        "expire_time": expire_time
    }
    return user_keys[user_id]

# ✅ API endpoint for game verification
@app.route("/verify", methods=["GET"])
def verify():
    key = request.args.get("key")
    device = request.args.get("device")
    if not key or not device:
        return jsonify({"status": "fail", "error": "Missing key or device"}), 400

    for uid, info in user_keys.items():
        if info["key"] == key:
            expire_time = datetime.datetime.strptime(info["expire_time"], "%Y-%m-%d %H:%M:%S")
            if expire_time > datetime.datetime.utcnow():
                return jsonify({"status": "ok"})
            else:
                return jsonify({"status": "fail", "error": "Expired key"}), 403
    return jsonify({"status": "fail", "error": "Invalid key"}), 403

# Telegram Bot Handlers
def getkey(update, context):
    user_id = str(update.effective_user.id)
    active_users.add(user_id)
    key_info = check_and_get_key(user_id)
    reply = f"🔑 Your 24H Key:\n\n`{key_info['key']}`\n\n⏰ Expire At (UTC): {key_info['expire_time']}"
    update.message.reply_text(reply, parse_mode="Markdown")

def start(update, context):
    update.message.reply_text("👋 Welcome to Odisha Hacker Key Bot!")
    getkey(update, context)

def allkeys(update, context):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ Not allowed.")
    if not user_keys:
        return update.message.reply_text("⚠️ No active keys.")
    text = "📋 *All Active Keys:*\n\n"
    for uid, info in user_keys.items():
        text += f"👤 User: `{uid}`\n🔑 `{info['key']}`\n⏰ {info['expire_time']}\n\n"
    update.message.reply_text(text, parse_mode="Markdown")

# Run Flask + Bot in parallel
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getkey", getkey))
    dp.add_handler(CommandHandler("allkeys", allkeys))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
