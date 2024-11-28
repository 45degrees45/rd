import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import tempfile
import subprocess
from main import run_tesseract, check_pre_requisites_tesseract
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
#TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_TOKEN = "7619738172:AAFg5f6mkoW1g9KPJMgSB-op8bEzCaayaNU"
VALID_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".gif", ".png", ".tif", ".bmp"]

# LLM configuration
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Small, efficient model
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class OCRBot:
    def __init__(self):
        # Check if tesseract is installed
        if not check_pre_requisites_tesseract():
            raise RuntimeError("Tesseract is not properly installed!")
        
        # Initialize LLM
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto",
            offload_folder="offload"
        )
        
        # Style options for responses
        self.style_options = {
            "formal": "Please respond in a formal, professional manner.",
            "casual": "Please respond in a casual, friendly tone.",
            "concise": "Please provide a brief, direct response.",
            "detailed": "Please provide a detailed, comprehensive response."
        }
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        welcome_message = (
            "👋 Welcome to the OCR & Chat Bot!\n\n"
            "Send me an image and I'll:\n"
            "1. Extract the text\n"
            "2. Let you choose a response style\n"
            "3. Generate an AI response\n\n"
            "Commands:\n"
            "/styles - View available response styles\n"
            "/help - Show this help message"
        )
        await update.message.reply_text(welcome_message)

    async def show_styles(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display available response styles."""
        keyboard = [[style] for style in self.style_options.keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("Choose a response style:", reply_markup=reply_markup)

    async def process_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process received images and extract text."""
        try:
            # Get the photo with highest resolution
            photo = update.message.photo[-1]
            
            # Download the photo
            file = await context.bot.get_file(photo.file_id)
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                await file.download_to_drive(temp_file.name)
                
                # Extract text using tesseract
                extracted_text = run_tesseract("image.jpg", None, temp_file.name)
                
                # Store text in context for later use
                context.user_data['extracted_text'] = extracted_text
                
                # Send extracted text to user
                await update.message.reply_text("📝 Extracted Text:\n\n" + extracted_text)
                
                # Show style options
                await self.show_styles(update, context)
                
            # Cleanup
            os.unlink(temp_file.name)
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            await update.message.reply_text("Sorry, there was an error processing your image.")

    async def generate_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate AI response based on extracted text and chosen style."""
        if 'extracted_text' not in context.user_data:
            await update.message.reply_text("Please send an image first!")
            return

        style = update.message.text.lower()
        if style not in self.style_options:
            return

        # Prepare prompt with style instruction
        prompt = f"{self.style_options[style]}\n\nText: {context.user_data['extracted_text']}\n\nResponse:"
        
        try:
            # Generate response using local LLM
            inputs = self.tokenizer(prompt, return_tensors="pt").to(DEVICE)
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
            )
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            await update.message.reply_text(f"🤖 AI Response ({style}):\n\n{response}")
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            await update.message.reply_text("Sorry, there was an error generating the response.")

    def run(self):
        """Run the bot."""
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.start))
        application.add_handler(CommandHandler("styles", self.show_styles))
        application.add_handler(MessageHandler(filters.PHOTO, self.process_image))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.generate_response))

        # Start the bot
        application.run_polling()

if __name__ == '__main__':
    bot = OCRBot()
    bot.run()
