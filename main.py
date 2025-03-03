import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
import config
from src.bot.handlers import start, button_callback, error_handler
from src.services.matcher import batch_match_teams

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    # Create the Application
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    logger.info("Starting bot with long polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
