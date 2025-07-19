#!/usr/bin/env python3
"""
Telegram Bot for Email Management with Brevo API
Main entry point for the application
"""

import os
import logging
from dotenv import load_dotenv
from telegram_bot import TelegramEmailBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the Telegram bot"""
    try:
        # Get bot token from environment
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        # Initialize and start the bot
        bot = TelegramEmailBot(bot_token)
        logger.info("Starting Telegram Email Bot...")
        bot.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
