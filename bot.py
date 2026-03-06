import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get('TOKEN')

async def start(update: Update, context):
    await update.message.reply_text("Hello! Haile's bot is alive.")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

def main():
    print("Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()

if __name__ == "__main__":
    main()