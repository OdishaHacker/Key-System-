from telegram.ext import Updater, CommandHandler
import os, random, string, datetime, atexit, signal, sys

# Bot Token from Environment Variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin ID (apna Telegram numeric ID daalna)
ADMIN_ID = 1973297878

# Memory-based key storage
user_keys = {}
active_users = set()

def generate_key():
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"ODISHA-HACKER-24H-{random_part}"

def check_and_get_key(user_id):
    now = datetime.datetime.utcnow()

    if user_id in user_keys:
        expire_time = datetime.datetime.strptime(user_keys[user_id]["expire_time"], "%Y-%m-%d %H:%M:%S")
        if expire_time > now:
            return user_keys[user_id]   # still valid

    # generate new key
    expire_time = (now + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    user_keys[user_id] = {
        "key": generate_key(),
        "expire_time": expire_time
    }
    return user_keys[user_id]

def getkey(update, context):
    user_id = str(update.effective_user.id)
    active_users.add(user_id)  # add to active users
    key_info = check_and_get_key(user_id)
    reply = f"🔑 Your 24H Key:\n{key_info['key']}\n\n⏰ Expire At (UTC): {key_info['expire_time']}"
    update.message.reply_text(reply, parse_mode="Markdown")

def start(update, context):
    user_id = str(update.effective_user.id)
    active_users.add(user_id)
    update.message.reply_text("👋 Welcome to Odisha Hacker Key Bot!")
    getkey(update, context)

# Admin command: view all keys
def allkeys(update, context):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return
    if not user_keys:
        update.message.reply_text("⚠️ No active keys found.")
        return
    text = "📋 *All Active Keys:*\n\n"
    for uid, info in user_keys.items():
        text += f"👤 User: {uid}\n🔑 {info['key']}\n⏰ {info['expire_time']}\n\n"
    update.message.reply_text(text, parse_mode="Markdown")

# Online/Offline message broadcast
def notify_all(context, message):
    for uid in list(active_users):
        try:
            context.bot.send_message(chat_id=uid, text=message)
        except:
            pass

def on_start(updater):
    # Send Online message to all active users
    notify_all(updater.bot, "✅ Bot is now Online!")

def on_shutdown(updater):
    try:
        notify_all(updater.bot, "⚠️ Bot is now Offline!")
    except:
        pass

# Setup bot
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("getkey", getkey))
dp.add_handler(CommandHandler("allkeys", allkeys))

# Run online message after bot starts
updater.job_queue.run_once(lambda ctx: on_start(updater), 1)

# Register shutdown handler
atexit.register(lambda: on_shutdown(updater))
signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

updater.start_polling()
updater.idle()
