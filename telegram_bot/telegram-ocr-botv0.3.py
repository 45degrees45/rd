import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import tempfile
from main import run_tesseract, check_pre_requisites_tesseract
import torch

# States
PHOTO, STYLE = range(2)

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRBot:
    def __init__(self):
        if not check_pre_requisites_tesseract():
            raise RuntimeError("Tesseract is not properly installed!")
        
        self.style_options = {
            "formal": "Formal and professional",
            "casual": "Casual and friendly",
            "concise": "Brief and direct",
            "detailed": "Comprehensive"
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start conversation and ask for photo."""
        welcome_message = (
            "Hi, I'm Wingman! 🤖\n\n"
            "Send me a screenshot and I'll:\n"
            "📸 Extract text\n"
            "🎯 Let you pick a style\n"
            "💬 Craft a response\n\n"
            "/cancel - Cancel operation"
        )
        await update.message.reply_text(welcome_message)
        return PHOTO

    async def photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the photo and extract text."""
        try:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                await file.download_to_drive(temp_file.name)
                extracted_text = run_tesseract("image.jpg", None, temp_file.name)
                os.unlink(temp_file.name)
                
                if not extracted_text.strip():
                    await update.message.reply_text("No text could be extracted. Please try another image.")
                    return PHOTO
                
                context.user_data['extracted_text'] = extracted_text
                await update.message.reply_text("📝 Extracted Text:\n\n" + extracted_text)
                
                # Show style options
                keyboard = [[style] for style in self.style_options.keys()]
                markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                await update.message.reply_text(
                    "Choose a response style:",
                    reply_markup=markup
                )
                return STYLE
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            await update.message.reply_text("Sorry, there was an error processing your image. Please try again.")
            return PHOTO

    async def style(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the style choice and generate response."""
        user_choice = update.message.text.lower()
        
        if user_choice not in self.style_options:
            await update.message.reply_text(
                "Please select a valid style from the keyboard.",
                reply_markup=ReplyKeyboardMarkup([[style] for style in self.style_options.keys()], one_time_keyboard=True)
            )
            return STYLE
        
        # For now, just echo back the text with style
        extracted_text = context.user_data.get('extracted_text', 'No text found')
        style_desc = self.style_options[user_choice]
        
        response = f"Style: {user_choice.capitalize()} ({style_desc})\n\n{extracted_text}"
        
        await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())
        
        # Clear conversation data
        context.user_data.clear()
        
        # Start fresh
        welcome_back = "Send another screenshot or use /cancel to exit."
        await update.message.reply_text(welcome_back)
        return PHOTO

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation."""
        context.user_data.clear()
        await update.message.reply_text(
            "Operation cancelled. Send /start to begin again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def run(self):
        """Run the bot."""
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                PHOTO: [MessageHandler(filters.PHOTO, self.photo)],
                STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.style)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        application.add_handler(conv_handler)
        application.run_polling()

if __name__ == '__main__':
    BOT_USERNAME = "wingmanbot"
    TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
    
    bot = OCRBot()
    bot.run()
