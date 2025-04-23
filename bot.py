
import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

DATA_FILE = "storage/data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Отправь /watch @username, чтобы следить за подписками.")

async def watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Укажи @username после команды.")
        return
    username = context.args[0].lstrip("@")
    chat_id = str(update.effective_chat.id)

    data = load_data()
    if chat_id not in data:
        data[chat_id] = []
    if username not in data[chat_id]:
        data[chat_id].append(username)
        save_data(data)
        await update.message.reply_text(f"✅ Теперь слежу за @{username}")
    else:
        await update.message.reply_text(f"🔁 Уже слежу за @{username}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("watch", watch))
    app.run_polling()
