import logging
import os
from datetime import datetime, timedelta
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
import config
from src.bot.handlers import start, button_callback, error_handler, try_match_teams
from src.services.matcher import batch_match_teams

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def match_teams_job(context):
    """Job to match teams every 2 hours"""
    logger.info("Running scheduled team matching job")
    
    # Match teams in batch
    matched_teams = batch_match_teams()
    logger.info(f"Matched {len(matched_teams)} teams")
    
    # Notify users about their teams
    for team, members in matched_teams:
        for user in members:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=context.bot_data["messages"].get_team_match_message(),
                    reply_markup=context.bot_data["keyboards"].get_confirmation_keyboard(team.id)
                )
            except Exception as e:
                logger.error(f"Failed to send message to user {user.telegram_id}: {e}")

def main():
    """Start the bot"""
    # Create the Application
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Store message and keyboard modules in bot_data for access in jobs
    from src.bot import messages, keyboards
    application.bot_data["messages"] = messages
    application.bot_data["keyboards"] = keyboards
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Add job to match teams every 2 hours
    job_queue = application.job_queue
    
    # Schedule the first run to be soon after startup
    first_run = datetime.now() + timedelta(minutes=1)
    
    # Then run every 2 hours
    job_queue.run_repeating(
        match_teams_job, 
        interval=timedelta(hours=2),
        first=first_run
    )
    
    logger.info(f"Scheduled team matching job to run every 2 hours, starting at {first_run}")
    
    # Start the Bot
    logger.info("Starting bot...")
    
    # Get port from environment variable (for Railway)
    port = int(os.environ.get('PORT', 8443))
    
    # Start the bot with webhook if on Railway (PORT is set)
    if 'PORT' in os.environ:
        # Use webhook when deployed
        railway_url = os.environ.get('RAILWAY_STATIC_URL')
        app_url = os.environ.get('APP_URL')
        
        if not app_url and railway_url:
            app_url = f"https://{railway_url}.up.railway.app"
        
        if not app_url:
            # Use the actual Railway app URL
            app_url = "https://hackathonteammatcher-production.up.railway.app"
            logger.info(f"Using hardcoded app URL: {app_url}")
        
        webhook_url = f"{app_url}/{config.TELEGRAM_BOT_TOKEN}"
        logger.info(f"Setting webhook URL to: {webhook_url}")
        
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=config.TELEGRAM_BOT_TOKEN,
            webhook_url=webhook_url
        )
    else:
        # Use polling for local development
        application.run_polling()

if __name__ == '__main__':
    main()
