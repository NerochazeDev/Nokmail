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
    
    async def send_simple_email(self, chat_id, email, subject, message):
        """Send a simple email"""
        try:
            result = await self.email_service.send_simple_email(
                to_email=email,
                to_name=email.split('@')[0].title(),
                subject=subject,
                message=message,
                user_id=chat_id
            )
            
            if result.get('success'):
                return f"✅ Email sent to {email}!"
            else:
                return f"❌ Failed to send email: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"
    
    def process_message(self, message):
        """Process incoming message"""
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        if text.startswith('/start'):
            response = """<b>Email Service Bot</b>

Welcome! This bot can send emails on your behalf.

<b>Commands:</b>
/email [email] [subject] | [message] - Send email
/help - Show this help message

Example: /email user@example.com Hello | This is a test message"""
            
        elif text.startswith('/email'):
            parts = text.split(' ', 1)
            if len(parts) > 1:
                email_command = parts[1].strip()
                # Parse: email subject | message
                if '|' in email_command:
                    email_part, message = email_command.split('|', 1)
                    email_parts = email_part.strip().split(' ', 1)
                    if len(email_parts) >= 2:
                        email = email_parts[0]
                        subject = email_parts[1]
                        message = message.strip()
                        
                        if '@' in email:
                            # Use asyncio to send email
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            response = loop.run_until_complete(self.send_simple_email(chat_id, email, subject, message))
                            loop.close()
                        else:
                            response = "❌ Please provide a valid email address.\nExample: /email user@example.com Hello | This is a test message"
                    else:
                        response = "❌ Please provide email and subject.\nExample: /email user@example.com Hello | This is a test message"
                else:
                    response = "❌ Please separate subject and message with '|'\nExample: /email user@example.com Hello | This is a test message"
            else:
                response = "❌ Please provide email details.\nExample: /email user@example.com Hello | This is a test message"
                
        elif text.startswith('/help'):
            response = """<b>Email Service Bot Help</b>

<b>Available Commands:</b>
/start - Welcome message
/email [email] [subject] | [message] - Send email
/help - Show this help

<b>Example Usage:</b>
/email user@example.com Hello World | This is my message content

The format is: /email [recipient] [subject] | [message content]
Use the pipe symbol | to separate subject from message."""
            
        else:
            response = "❓ Unknown command. Use /help to see available commands."
        
        return response
    
    def run(self):
        """Run the bot"""
        print("Email Service Bot Starting...")
        print("Service is running! Send /start to begin.")
        
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