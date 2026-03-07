import os
import sys
import tempfile
from datetime import datetime
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup

# Your portfolio URL
PORTFOLIO_URL = "https://haile-portfolio-theta.vercel.app/"

def fetch_portfolio_data():
    """Fetch and parse information from portfolio website"""
    try:
        response = requests.get(PORTFOLIO_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract information
        data = {
            'name': 'Haile',  # Default fallback
            'title': 'IT Instructor & Developer',
            'location': 'Addis Ababa',
            'education': 'CS Graduate',
            'experience_years': '1+ year teaching, 6+ months field experience',
            'skills': {
                'networking': ['Cisco IOS', 'Routing', 'Switching', 'Firewalls', 'TCP/IP'],
                'programming': ['Python', 'Java', 'C++', 'JavaScript', 'TypeScript'],
                'mobile': ['Flutter', 'Firebase', 'Dart'],
                'devops': ['Docker', 'Linux'],
                'it_support': ['Hardware', 'OS Support', 'Diagnostics']
            },
            'projects': [
                'Network Configuration Lab Setup',
                'Flutter-Based Mobile Application',
                'GPS Installation & Tracking Workflow'
            ]
        }
        
        # Try to extract from website if possible
        # This is a simplified version - actual extraction would need more specific parsing
        
        return data
    except Exception as e:
        print(f"Error fetching portfolio: {e}")
        # Return default data if fetch fails
        return get_default_portfolio_data()

def get_default_portfolio_data():
    """Default portfolio data as fallback"""
    return {
        'name': 'Haile',
        'title': 'IT Instructor & Developer',
        'location': 'Addis Ababa',
        'education': 'CS Graduate',
        'experience_years': '1+ year teaching, 6+ months field experience',
        'skills': {
            'networking': ['Cisco IOS', 'Routing', 'Switching', 'Firewalls'],
            'programming': ['Python', 'Java', 'C++', 'JavaScript'],
            'mobile': ['Flutter', 'Firebase', 'Dart'],
            'devops': ['Docker'],
            'it_support': ['Hardware', 'OS Support']
        },
        'projects': [
            'Network Configuration Lab Setup',
            'Flutter Mobile App',
            'GPS Installation Workflow'
        ]
    }

# Load portfolio data once at startup
portfolio_data = fetch_portfolio_data()
print("✅ Portfolio data loaded")

print("Starting bot...")
print(f"Python version: {sys.version}")

# Get tokens from environment variables
TELEGRAM_TOKEN = os.environ.get('TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Debug: Print if tokens are found
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
    # Try different model names
    model_names = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
    model = None
    
    for model_name in model_names:
        try:
            print(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            # Test the model
            test_response = model.generate_content("Say 'OK'")
            print(f"✅ Successfully using model: {model_name}")
            break
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
    
    if model is None:
        print("❌ No working Gemini model found!")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Gemini configuration error: {e}")
    sys.exit(1)

# Conversation states
JOB_TITLE, COMPANY, REQUIREMENTS, SKILLS, EXPERIENCE = range(5)

# Store user data temporarily
user_data = {}

# Your Telegram ID for private access
YOUR_ID = 6673503943  # Your actual ID

def is_authorized(user_id):
    """Check if user is authorized (only you)"""
    return user_id == YOUR_ID

# PDF Generator Class with Unicode support using built-in fonts
class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, f'Job Application Documents - {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_cv_pdf(data):
    """Create a PDF CV from the collected data"""
    pdf = PDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 10, f"CV for {data['job_title']}", 0, 1, 'C')
    pdf.ln(10)
    
    # Personal Info (using portfolio data)
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, "Personal Information", 0, 1)
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 10, f"Name: {portfolio_data['name']}", 0, 1)
    pdf.cell(0, 10, f"Title: {portfolio_data['title']}", 0, 1)
    pdf.cell(0, 10, f"Location: {portfolio_data['location']}", 0, 1)
    pdf.cell(0, 10, f"Education: {portfolio_data['education']}", 0, 1)
    pdf.cell(0, 10, f"Email: haileyesusshibru19@gmail.com", 0, 1)
    pdf.cell(0, 10, f"Position: {data['job_title']}", 0, 1)
    pdf.cell(0, 10, f"Company: {data['company']}", 0, 1)
    pdf.ln(5)
    
    # Professional Summary
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, "Professional Summary", 0, 1)
    pdf.set_font('DejaVu', '', 11)
    pdf.multi_cell(0, 6, f"Passionate {data['job_title']} with {data['experience']} of experience. Skilled in {data['skills']} and dedicated to delivering high-quality results.")
    pdf.ln(5)
    
    # Key Qualifications
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, "Key Qualifications", 0, 1)
    pdf.set_font('DejaVu', '', 11)
    
    # Split requirements into bullet points (using asterisks instead of •)
    requirements_list = data['requirements'].split(',')
    for req in requirements_list[:5]:
        pdf.cell(10)
        pdf.cell(0, 6, f"- {req.strip()}", 0, 1)
    pdf.ln(5)
    
    # Technical Skills
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, "Technical Skills", 0, 1)
    pdf.set_font('DejaVu', '', 11)

    # Format skills by category from portfolio data
    for category, skills in portfolio_data['skills'].items():
        pdf.set_font('DejaVu', 'B', 11)
        pdf.cell(0, 6, f"{category.title()}:", 0, 1)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(10)  # Indent
        pdf.cell(0, 6, ", ".join(skills), 0, 1)
    pdf.ln(5)
    
    # Experience
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, "Experience", 0, 1)
    pdf.set_font('DejaVu', '', 11)
    pdf.multi_cell(0, 6, f"• {data['experience']} of relevant experience")
    pdf.multi_cell(0, 6, "• Developed projects demonstrating expertise in required technologies")
    pdf.multi_cell(0, 6, "• Collaborated with teams to deliver solutions meeting client requirements")
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name

def create_cover_letter_pdf(data):
    """Create a PDF cover letter from the collected data"""
    pdf = PDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 10, "Cover Letter", 0, 1, 'C')
    pdf.ln(10)
    
    # Date
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 6, datetime.now().strftime("%B %d, %Y"), 0, 1)
    pdf.ln(10)
    
    # Recipient
    pdf.multi_cell(0, 6, f"Hiring Manager\n{data['company']}\n[Company Address]")
    pdf.ln(10)
    
    # Subject
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(0, 6, f"Re: Application for {data['job_title']} Position", 0, 1)
    pdf.ln(10)
    
    # Body - UPDATED with portfolio data
    pdf.set_font('DejaVu', '', 11)
    
    # Create a skills summary from portfolio data
    all_skills = []
    for category, skills in portfolio_data['skills'].items():
        all_skills.extend(skills)
    skills_summary = ", ".join(all_skills[:10])  # Top 10 skills
    
    body = f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {data['job_title']} position at {data['company']}. As an {portfolio_data['title']} based in {portfolio_data['location']} with {portfolio_data['experience_years']}, I am confident in my ability to contribute effectively to your team.

My background includes:
• {portfolio_data['experience_years']} of teaching and practical experience
• Expertise in: {skills_summary}
• {portfolio_data['education']} in Computer Science

Your requirement for {data['requirements']} aligns perfectly with my background. I have {data['experience']} of experience developing solutions and working with teams to deliver high-quality results.

Key qualifications I bring:
- Expertise in {data['skills']}
- Proven track record of meeting requirements like {data['requirements']}
- Strong commitment to learning and growth
- Excellent problem-solving and communication skills

I would welcome the opportunity to discuss how my skills and experience align with {data['company']}'s needs. Thank you for considering my application.

Best regards,
{portfolio_data['name']}
{portfolio_data['title']}
haileyesusshibru19@gmail.com
{portfolio_data['location']}
    """
    
    pdf.multi_cell(0, 6, body)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name

async def start(update: Update, context):
    """Welcome message with buttons"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("🔒 This is a private bot. You are not authorized.")
        return
    
    user = update.effective_user
    welcome_message = f"""
👋 **Hello {user.first_name}! Welcome to your Job Application Assistant!**

I can help you create professional CVs and cover letters in PDF format!

📄 **Features:**
• Create customized CVs as PDF
• Generate tailored cover letters as PDF
• AI-powered content generation
• Save and download files directly

**What would you like to create?**
    """
    
    keyboard = [
        [InlineKeyboardButton("📄 Create CV", callback_data="create_cv")],
        [InlineKeyboardButton("✉️ Create Cover Letter", callback_data="create_cover")],
        [InlineKeyboardButton("📁 Portfolio", url="https://haile-portfolio-theta.vercel.app/")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)

async def create_cv_start(update: Update, context):
    """Start CV creation process"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        "📄 **Let's create your CV!**\n\n"
        "Please answer a few questions:\n\n"
        "**What job title are you applying for?**\n"
        "(Example: Python Developer, Junior Programmer)"
    )
    return JOB_TITLE

async def create_cover_start(update: Update, context):
    """Start cover letter creation process"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        "✉️ **Let's create your cover letter!**\n\n"
        "Please answer a few questions:\n\n"
        "**What job title are you applying for?**"
    )
    return JOB_TITLE

async def get_job_title(update: Update, context):
    """Get job title from user"""
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    
    user_data[user_id]['job_title'] = update.message.text
    
    await update.message.reply_text(
        f"📌 Job title: **{update.message.text}**\n\n"
        "**What company are you applying to?**"
    )
    return COMPANY

async def get_company(update: Update, context):
    """Get company name from user"""
    user_id = update.message.from_user.id
    user_data[user_id]['company'] = update.message.text
    
    await update.message.reply_text(
        f"🏢 Company: **{update.message.text}**\n\n"
        "**What are the key requirements from the job posting?**\n"
        "(List skills separated by commas)"
    )
    return REQUIREMENTS

async def get_requirements(update: Update, context):
    """Get job requirements from user"""
    user_id = update.message.from_user.id
    user_data[user_id]['requirements'] = update.message.text
    
    await update.message.reply_text(
        "✅ **Great! Now tell me about your relevant skills:**\n"
        "(List your skills separated by commas: Python, Communication, etc.)"
    )
    return SKILLS

async def get_skills(update: Update, context):
    """Get user skills"""
    user_id = update.message.from_user.id
    user_data[user_id]['skills'] = update.message.text
    
    await update.message.reply_text(
        "📊 **How many years of relevant experience do you have?**\n"
        "(Example: 2 years, 3+ years)"
    )
    return EXPERIENCE

async def generate_pdfs(update: Update, context):
    """Generate and send PDF files"""
    user_id = update.message.from_user.id
    user_data[user_id]['experience'] = update.message.text
    
    data = user_data[user_id]
    
    await update.message.reply_text("⏳ **Generating your PDF documents...**")
    
    try:
        # Create PDFs
        cv_pdf_path = create_cv_pdf(data)
        cover_pdf_path = create_cover_letter_pdf(data)
        
        # Send CV PDF
        with open(cv_pdf_path, 'rb') as cv_file:
            await update.message.reply_document(
                document=cv_file,
                filename=f"CV_{data['job_title'].replace(' ', '_')}.pdf",
                caption="📄 **Your customized CV**"
            )
        
        # Send Cover Letter PDF
        with open(cover_pdf_path, 'rb') as cover_file:
            await update.message.reply_document(
                document=cover_file,
                filename=f"Cover_Letter_{data['job_title'].replace(' ', '_')}.pdf",
                caption="✉️ **Your customized cover letter**"
            )
        
        # Clean up temporary files
        os.unlink(cv_pdf_path)
        os.unlink(cover_pdf_path)
        
        # Ask what to do next
        keyboard = [
            [InlineKeyboardButton("📄 New CV", callback_data="create_cv")],
            [InlineKeyboardButton("✉️ New Cover Letter", callback_data="create_cover")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ **Documents generated successfully!**\n\n"
            "You can download the PDF files above.\n\n"
            "What would you like to do next?",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Error generating PDFs:** {str(e)}")
        print(f"PDF Generation Error: {e}")
    
    finally:
        # Clear user data
        if user_id in user_data:
            del user_data[user_id]
    
    return ConversationHandler.END

async def cancel(update: Update, context):
    """Cancel conversation"""
    user_id = update.message.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    
    await update.message.reply_text("❌ Operation cancelled. Use /start to begin again.")
    return ConversationHandler.END

async def help_command(update: Update, context):
    """Show help menu"""
    if not is_authorized(update.effective_user.id):
        return
    
    help_text = """
📋 **Available Commands:**

/start - Main menu
/createcv - Start CV creation
/createcover - Start cover letter
/help - Show this help

**How it works:**
1. Click "Create CV" or "Create Cover Letter"
2. Answer a few questions about the job
3. Get professional PDF files ready to use!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_callback(update: Update, context):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command(update, context)
    elif query.data == "create_cv":
        await create_cv_start(update, context)
        return JOB_TITLE
    elif query.data == "create_cover":
        await create_cover_start(update, context)
        return JOB_TITLE
    elif query.data == "menu":
        await start(update, context)

def main():
    """Main function to run the bot"""
    print("Building application...")
    
    if not TELEGRAM_TOKEN:
        print("❌ Cannot start: TELEGRAM_TOKEN is missing")
        return
    
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        print("✅ Application built successfully")
    except Exception as e:
        print(f"❌ Failed to build application: {e}")
        return
    
    # Conversation handler for CV/Cover Letter
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(create_cv_start, pattern="^create_cv$"),
            CallbackQueryHandler(create_cover_start, pattern="^create_cover$"),
            CommandHandler("createcv", create_cv_start),
            CommandHandler("createcover", create_cover_start)
        ],
        states={
            JOB_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_job_title)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
            REQUIREMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_requirements)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_skills)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_pdfs)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("✅ Bot is running! PDF generation ready.")
    print("🤖 Send /start to create CVs and cover letters!")
    app.run_polling()

if __name__ == "__main__":
    main()
