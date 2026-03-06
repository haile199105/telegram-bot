import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

print("Starting bot...")
print(f"Python version: {sys.version}")

TOKEN = os.environ.get('TOKEN')

if TOKEN is None:
    print("ERROR: TOKEN environment variable not set!")
    sys.exit(1)
else:
    print(f"Token loaded: {TOKEN[:5]}...{TOKEN[-5:]}")

# /start command
async def start(update: Update, context):
    user = update.effective_user
    welcome_message = f"👋 Hello {user.first_name}! Welcome to my personal bot.\n\nI'm Haile's assistant bot. Use /help to see what I can do."
    
    # Create a simple keyboard
    keyboard = [
        [InlineKeyboardButton("📁 Portfolio", url="https://haile199105.github.io/Portfolio1/")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# /help command
async def help_command(update: Update, context):
    help_text = """
📋 **Available Commands:**

/start - Welcome message
/help - Show this help menu
/about - About Haile
/portfolio - View my portfolio website
/contact - Get contact information
/job - Job search status

💡 Just type any command above!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# /about command
async def about(update: Update, context):
    about_text = """
👨‍💻 **About Haile**

I'm a passionate developer learning to build cool things with code.

🔧 **Skills:**
- Python Programming
- Telegram Bots
- Web Development
- Problem Solving

🌱 Currently learning more every day!
    """
    await update.message.reply_text(about_text, parse_mode='Markdown')

# /portfolio command
async def portfolio(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("🌐 Visit My Portfolio", url="https://haile-portfolio-theta.vercel.app/")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Click the button below to check out my portfolio!",
        reply_markup=reply_markup
    )

# /contact command
async def contact(update: Update, context):
    contact_text = """
📬 **Contact Haile**

📧 Email: haileyesusshibru19@gmail.com
💼 GitHub: github.com/haile199105
📱 Telegram: @haile199105

Feel free to reach out!
    """
    await update.message.reply_text(contact_text, parse_mode='Markdown')

# /job command - useful for your job search
async def job_status(update: Update, context):
    job_text = """
💼 **Job Search Status**

🔍 Currently looking for opportunities in:
- Python Development
- Entry Level Programming
- Tech Support

📊 **Status:** Actively looking
⭐ **Open to:** Remote, Hybrid, On-site

Send /contact to reach me!
    """
    await update.message.reply_text(job_text, parse_mode='Markdown')

# Handle button clicks
async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command(update, context)

# Echo function (optional - you can keep or remove)
async def echo(update: Update, context):
    # Only echo if it's not a command
    if not update.message.text.startswith('/'):
        await update.message.reply_text(f"You said: {update.message.text}")

def main():
    print("Building application...")
    app = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("job", job_status))
    
    # Add button callback handler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Optional: keep echo for non-commands
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("Bot is polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
