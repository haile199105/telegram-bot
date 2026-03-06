import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

print("Starting bot...")
print(f"Python version: {sys.version}")

TOKEN = os.environ.get('TOKEN')

if TOKEN is None:
    print("ERROR: TOKEN environment variable not set!")
    sys.exit(1)
else:
    print(f"Token loaded: {TOKEN[:5]}...{TOKEN[-5:]}")

async def start(update: Update, context):
    print(f"Start command from {update.effective_user.username}")
    await update.message.reply_text("Hello! Haile's bot is alive!")

async def echo(update: Update, context):
    print(f"Echo: {update.message.text}")
    await update.message.reply_text(update.message.text)

def main():
    print("Building application...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot is polling...")
    app.run_polling()

if __name__ == "__main__":
    main()