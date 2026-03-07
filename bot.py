import os
import sys
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler

print("Starting bot...")
print(f"Python version: {sys.version}")

# Get tokens from environment variables
TELEGRAM_TOKEN = os.environ.get('TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Debug: Print if tokens are found (hiding most of the token for security)
print(f"TELEGRAM_TOKEN found: {'Yes' if TELEGRAM_TOKEN else 'No'}")
if TELEGRAM_TOKEN:
    print(f"TELEGRAM_TOKEN starts with: {TELEGRAM_TOKEN[:5]}...")
else:
    print("ERROR: TELEGRAM_TOKEN is missing!")
    sys.exit(1)

print(f"GEMINI_API_KEY found: {'Yes' if GEMINI_API_KEY else 'No'}")
if GEMINI_API_KEY:
    print(f"GEMINI_API_KEY starts with: {GEMINI_API_KEY[:5]}...")
else:
    print("ERROR: GEMINI_API_KEY is missing!")
    sys.exit(1)

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini configured successfully")
except Exception as e:
    print(f"❌ Gemini configuration error: {e}")
    sys.exit(1)

# Store conversation history for each user
user_conversations = {}

# Your Telegram ID for private access
YOUR_ID = 6673503943  # ⚠️ REPLACE WITH YOUR ACTUAL TELEGRAM ID!
print(f"Your Telegram ID set to: {YOUR_ID}")

def is_authorized(user_id):
    """Check if user is authorized (only you)"""
    return user_id == YOUR_ID

async def start(update: Update, context):
    """Welcome message with buttons"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("🔒 This is a private bot. You are not authorized.")
        return
    
    user = update.effective_user
    welcome_message = f"""
👋 **Hello {user.first_name}! Welcome to your AI-powered bot!**

I'm integrated with Google's **Gemini AI**! Here's what I can do:

🤖 **Chat with AI** - Just send me any message and I'll respond intelligently
📝 **Commands** - Use the buttons below or type commands

**Try it:** Just send me any question!
    """
    
    keyboard = [
        [InlineKeyboardButton("🤖 Ask AI", callback_data="ai_chat")],
        [InlineKeyboardButton("📁 Portfolio", url="https://haile-portfolio-theta.vercel.app/")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context):
    """Show help menu"""
    if not is_authorized(update.effective_user.id):
        return
    
    help_text = """
📋 **Available Commands:**

/start - Main menu
/help - Show this help
/clear - Clear conversation history
/about - About me
/portfolio - My portfolio
/contact - Contact info
/job - Job status

**AI Chat:**
Just send any message and I'll respond using Gemini AI!
Use /clear to reset the conversation.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def clear_command(update: Update, context):
    """Clear conversation history"""
    if not is_authorized(update.effective_user.id):
        return
    
    user_id = update.effective_user.id
    if user_id in user_conversations:
        del user_conversations[user_id]
    
    await update.message.reply_text("🧹 Conversation history cleared! Let's start fresh.")

async def about(update: Update, context):
    """About you"""
    if not is_authorized(update.effective_user.id):
        return
    
    about_text = """
👨‍💻 **About Me**

I'm Haile, a developer passionate about AI and automation.

🔧 **Skills:**
- Python Programming
- AI Integration (Gemini)
- Telegram Bots
- Web Development

🌱 Currently learning and building!
    """
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def portfolio(update: Update, context):
    """Portfolio link"""
    if not is_authorized(update.effective_user.id):
        return
    
    keyboard = [
        [InlineKeyboardButton("🌐 Visit My Portfolio", url="https://haile-portfolio-theta.vercel.app/")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Click the button below to check out my portfolio!",
        reply_markup=reply_markup
    )

async def contact(update: Update, context):
    """Contact information"""
    if not is_authorized(update.effective_user.id):
        return
    
    contact_text = """
📬 **Contact Info**

📧 Email: haileyesusshibru19@gmail.com
💼 GitHub: github.com/haile199105
📱 Telegram: @haile199105
    """
    await update.message.reply_text(contact_text, parse_mode='Markdown')

async def job_status(update: Update, context):
    """Job search status"""
    if not is_authorized(update.effective_user.id):
        return
    
    job_text = """
💼 **Job Search Status**

🔍 Looking for opportunities in:
- Python Development
- AI/ML Integration
- Bot Development

📊 **Status:** Actively looking
⭐ **Open to:** Remote, Hybrid, On-site
    """
    await update.message.reply_text(job_text, parse_mode='Markdown')

async def handle_message(update: Update, context):
    """Handle regular messages with Gemini AI"""
    if not is_authorized(update.effective_user.id):
        return
    
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Initialize conversation history for new users
        if user_id not in user_conversations:
            user_conversations[user_id] = []
        
        # Add user message to history
        user_conversations[user_id].append(f"User: {user_message}")
        
        # Keep only last 10 messages for context (to avoid token limits)
        if len(user_conversations[user_id]) > 10:
            user_conversations[user_id] = user_conversations[user_id][-10:]
        
        # Create context prompt
        context_history = "\n".join(user_conversations[user_id])
        prompt = f"""You are a helpful AI assistant integrated into a Telegram bot. 
        Have a natural conversation with the user.
        
        Conversation history:
        {context_history}
        
        Respond naturally and helpfully:"""
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        ai_response = response.text
        
        # Add AI response to history
        user_conversations[user_id].append(f"Assistant: {ai_response}")
        
        # Send response (split if too long)
        if len(ai_response) > 4000:
            for i in range(0, len(ai_response), 4000):
                await update.message.reply_text(ai_response[i:i+4000])
        else:
            await update.message.reply_text(ai_response)
            
    except Exception as e:
        error_message = f"❌ Error getting AI response: {str(e)}"
        await update.message.reply_text(error_message)
        print(f"Gemini API Error: {e}")

async def button_callback(update: Update, context):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command(update, context)
    elif query.data == "ai_chat":
        await query.message.reply_text(
            "🤖 **AI Chat Mode**\n\nJust send me any message and I'll respond using Gemini AI!\n"
            "Use /clear to reset the conversation."
        )

def main():
    """Main function to run the bot"""
    print("Building application...")
    
    # Verify token before building app
    if not TELEGRAM_TOKEN:
        print("❌ Cannot start: TELEGRAM_TOKEN is missing")
        return
    
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        print("✅ Application built successfully")
    except Exception as e:
        print(f"❌ Failed to build application: {e}")
        return
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("job", job_status))
    
    # Handle regular messages (non-commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Handle button callbacks
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    print("🤖 Gemini AI is active - send any message to chat!")
    app.run_polling()

if __name__ == "__main__":
    main()
