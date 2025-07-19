#!/usr/bin/env python3
"""
Test script to verify email sending functionality with Brevo API
"""

import os
import requests
from dotenv import load_dotenv
from email_service import EmailService
from client_manager import ClientManager

# Load environment variables
load_dotenv()

def test_email_sending():
    """Test sending an email to verify the setup works"""
    
    # Check if required environment variables are set
    brevo_key = os.getenv('BREVO_API_KEY')
    sender_email = os.getenv('DEFAULT_SENDER_EMAIL')
    sender_name = os.getenv('DEFAULT_SENDER_NAME')
    
    print("=== Email Service Test ===")
    print(f"Brevo API Key: {'✓ Set' if brevo_key else '✗ Missing'}")
    print(f"Sender Email: {sender_email or '✗ Missing'}")
    print(f"Sender Name: {sender_name or '✗ Missing'}")
    print()
    
    if not all([brevo_key, sender_email, sender_name]):
        print("❌ Missing required environment variables")
        return False
    
    # Initialize services
    email_service = EmailService()
    client_manager = ClientManager()
    
    # Test user ID (for rate limiting)
    test_user_id = 12345
    
    # Test email details
    test_email = "ayinlasalami6@gmail.com"
    test_name = "Test User"
    test_subject = "WalletSecure Test Email"
    template_name = "welcome_email"
    
    print(f"Sending test email to: {test_email}")
    print(f"Subject: {test_subject}")
    print(f"Template: {template_name}")
    print()
    
    try:
        # Send the email
        result = email_service.send_email(
            to_email=test_email,
            to_name=test_name,
            subject=test_subject,
            template_name=template_name,
            user_id=test_user_id
        )
        
        if result.get('success'):
            print("✅ Email sent successfully!")
            print(f"Message ID: {result.get('message_id', 'N/A')}")
            return True
        else:
            print("❌ Email sending failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == '__main__':
    # Run the test (this will be async in the actual service)
    import asyncio
    
    async def run_test():
        email_service = EmailService()
        
        result = await email_service.send_email(
            to_email="ayinlasalami6@gmail.com",
            to_name="Test User",
            subject="WalletSecure Test Email",
            template_name="welcome_email",
            user_id=12345
        )
        
        if result.get('success'):
            print("✅ Email sent successfully!")
            print(f"Message ID: {result.get('message_id', 'N/A')}")
        else:
            print("❌ Email sending failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        return result
    
    asyncio.run(run_test())