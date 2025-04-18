from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient
from datetime import datetime
import logging
import os

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["KENZU"]
collection = db["ULP"]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /insert <data> to add or /get to retrieve your data.")

# /insert
async def insert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide data. Usage: /insert <data>")
        return

    data = " ".join(context.args)
    user = update.message.from_user

    doc = {
        "user_id": user.id,
        "username": user.username,
        "data": data,
        "timestamp": datetime.utcnow()
    }

    result = collection.insert_one(doc)
    logger.info(f"Inserted data from {user.username}: {data}")
    await update.message.reply_text(f"Data saved! ID: {result.inserted_id}")

# /get
async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    documents = collection.find({"user_id": user_id}).sort("timestamp", -1).limit(5)
    reply = "\n".join([f"- {doc['data']} ({doc['timestamp']})" for doc in documents])
    await update.message.reply_text(reply or "No data found.")

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("insert", insert))
    app.add_handler(CommandHandler("get", get))
    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()