"""
Configuration settings for the Telegram Email Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Brevo API Configuration
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'

# Email Configuration
DEFAULT_SENDER_EMAIL = os.getenv('DEFAULT_SENDER_EMAIL', 'noreply@example.com')
DEFAULT_SENDER_NAME = os.getenv('DEFAULT_SENDER_NAME', 'Bot Mailer')

# Button URL Configuration
BLOCK_DEVICE_URL = os.getenv('BLOCK_DEVICE_URL', 'https://your-security-portal.com')

# File paths
CLIENTS_FILE = 'data/clients.json'
EMAIL_LOG_FILE = 'data/email_log.json'
TEMPLATES_DIR = 'templates'

# Rate limiting (emails per minute)
EMAIL_RATE_LIMIT = int(os.getenv('EMAIL_RATE_LIMIT', '10'))

# Bot settings
MAX_CLIENTS_PER_USER = int(os.getenv('MAX_CLIENTS_PER_USER', '100'))
ADMIN_USER_IDS = [int(x) for x in os.getenv('ADMIN_USER_IDS', '').split(',') if x.strip()]
