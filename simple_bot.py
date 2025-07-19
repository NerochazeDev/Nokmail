#!/usr/bin/env python3
"""
Simplified Telegram Bot that works around import issues
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from email_service import EmailService
from client_manager import ClientManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class SimpleTelegramBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.email_service = EmailService()
        self.client_manager = ClientManager()
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    async def send_test_email(self, to_email: str, to_name: str = None):
        """Send a test email"""
        if not to_name:
            to_name = to_email.split('@')[0]
        
        result = await self.email_service.send_email(
            to_email=to_email,
            to_name=to_name,
            subject="Test Email from WalletSecure Bot",
            template_name="welcome_email",
            user_id=12345
        )
        
        return result
    
    def add_test_client(self, email: str, name: str = None):
        """Add a test client"""
        if not name:
            name = email.split('@')[0]
        
        try:
            client_id = self.client_manager.add_client(12345, name, email)
            return {"success": True, "client_id": client_id, "name": name, "email": email}
        except Exception as e:
            return {"success": False, "error": str(e)}

async def test_bot_functionality():
    """Test bot functionality"""
    print("=== Testing Bot Functionality ===")
    
    try:
        bot = SimpleTelegramBot()
        print("✓ Bot initialized successfully")
        
        # Test adding a client
        test_email = "ayinlasalami6@gmail.com"
        test_name = "Ayinla Salami"
        
        print(f"\nAdding test client: {test_name} ({test_email})")
        client_result = bot.add_test_client(test_email, test_name)
        
        if client_result["success"]:
            print(f"✓ Client added with ID: {client_result['client_id']}")
        else:
            print(f"⚠ Client might already exist: {client_result['error']}")
        
        # Test sending email
        print(f"\nSending test email to: {test_email}")
        email_result = await bot.send_test_email(test_email, test_name)
        
        if email_result["success"]:
            print(f"✓ Email sent successfully!")
            print(f"  Message ID: {email_result.get('message_id', 'N/A')}")
        else:
            print(f"✗ Email failed: {email_result.get('error', 'Unknown error')}")
        
        # Show available templates
        templates = bot.email_service.get_available_templates()
        print(f"\nAvailable email templates:")
        for template in templates:
            print(f"  • {template['name']} - {template['description']}")
        
        # Show stats
        stats = bot.email_service.get_user_stats(12345)
        print(f"\nEmail statistics:")
        print(f"  • Total sent: {stats['total_sent']}")
        print(f"  • Successful: {stats['successful_sends']}")
        print(f"  • Failed: {stats['failed_sends']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == '__main__':
    asyncio.run(test_bot_functionality())