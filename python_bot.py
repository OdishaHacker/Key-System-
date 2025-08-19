from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json, os, random, string, datetime

# 🔑 BOT_TOKEN ab environment variable se aayega
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "keys.json"

def load_db():
    return json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else {}

def save_db(data):
    json.dump(data, open(DB_FILE, "w"), indent=4)

def generate_key():
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"ODISHA-HACKER-24H-{random_part}"

def getkey(update, context):
    user_id = str(update.effective_user.id)
    db = load_db()

    if user_id not in db:
        expire_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        db[user_id] = {
            "key": generate_key(),
            "expire_time": expire_time
        }
        save_db(db)

    key_info = db[user_id]
    reply = f"🔑 Your 24H Key:\n`{key_info['key']}`\n\n⏰ Expire At (UTC): {key_info['expire_time']}"
    update.message.reply_text(reply, parse_mode="Markdown")

def start(update, context):
    update.message.reply_text("👋 Welcome to Odisha Hacker Key Bot!")
    getkey(update, context)

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("getkey", getkey))

updater.start_polling()
updater.idle()
