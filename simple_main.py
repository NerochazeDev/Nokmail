#!/usr/bin/env python3
"""
Simple Telegram Bot Starter for Email Management
Direct approach without complex imports
"""

import os
import requests
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from email_service import EmailService
from client_manager import ClientManager

# Load environment variables
load_dotenv()

class SimpleTelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.email_service = EmailService()
        self.client_manager = ClientManager()
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
    def send_message(self, chat_id, text):
        """Send a message to Telegram chat"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data)
        return response.json()
    
    def get_updates(self, offset=0):
        """Get updates from Telegram"""
        url = f"{self.base_url}/getUpdates"
        params = {'offset': offset, 'timeout': 30}
        response = requests.get(url, params=params)
        return response.json()
    
    async def send_security_alert(self, chat_id, email):
        """Send security alert email"""
        try:
            locations = ['Beijing, China', 'Shanghai, China', 'Karachi, Pakistan', 
                        'Lahore, Pakistan', 'Mumbai, India', 'Delhi, India',
                        'Dhaka, Bangladesh', 'Kathmandu, Nepal', 'Colombo, Sri Lanka']
            
            import random
            alert_data = {
                'login_location': random.choice(locations),
                'ip_address': f"{random.randint(100,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'device_info': random.choice(['Unknown Windows Device', 'Unknown Android Device', 'Unknown iPhone']),
                'browser_info': random.choice(['Chrome 120.0', 'Safari 17.2', 'Firefox 121.0']),
                'login_time': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                'alert_time': datetime.now().strftime('%I:%M %p UTC'),
                'alert_id': f'WS{random.randint(100000, 999999)}'
            }
            
            result = await self.email_service.send_email(
                to_email=email,
                to_name=email.split('@')[0].title(),
                subject="Account Security Notice - Login Verification Required",
                template_name="security_alert",
                user_id=99999,
                **alert_data
            )
            
            if result.get('success'):
                return f"✅ Security alert sent to {email}!\nAlert ID: {alert_data['alert_id']}\nLocation: {alert_data['login_location']}"
            else:
                return f"❌ Failed to send alert: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ Error sending alert: {str(e)}"
    
    def process_message(self, message):
        """Process incoming message"""
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        if text.startswith('/start'):
            response = """🔒 <b>WalletSecure Security Bot</b>

Welcome! This bot can send security alerts for suspicious login attempts.

<b>Commands:</b>
/alert [email] - Send security alert to email
/help - Show this help message

Example: /alert user@example.com"""
            
        elif text.startswith('/alert'):
            parts = text.split(' ', 1)
            if len(parts) > 1:
                email = parts[1].strip()
                if '@' in email:
                    # Use asyncio to send alert
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(self.send_security_alert(chat_id, email))
                    loop.close()
                else:
                    response = "❌ Please provide a valid email address.\nExample: /alert user@example.com"
            else:
                response = "❌ Please provide an email address.\nExample: /alert user@example.com"
                
        elif text.startswith('/help'):
            response = """🔒 <b>WalletSecure Security Bot Help</b>

<b>Available Commands:</b>
• /start - Welcome message
• /alert [email] - Send security alert
• /help - Show this help

<b>Example Usage:</b>
/alert ayinlasalami6@gmail.com

The bot will send a professional security alert email about suspicious login attempts from locations like China, Pakistan, or India."""
            
        else:
            response = "❓ Unknown command. Use /help to see available commands."
        
        return response
    
    def run(self):
        """Run the bot"""
        print("🔒 WalletSecure Security Bot Starting...")
        print("Bot is running! Send /start to begin.")
        
        offset = 0
        while True:
            try:
                updates = self.get_updates(offset)
                
                if updates.get('ok'):
                    for update in updates.get('result', []):
                        offset = update['update_id'] + 1
                        
                        if 'message' in update:
                            message = update['message']
                            response = self.process_message(message)
                            self.send_message(message['chat']['id'], response)
                            
            except KeyboardInterrupt:
                print("\n👋 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

if __name__ == '__main__':
    bot = SimpleTelegramBot()
    bot.run()