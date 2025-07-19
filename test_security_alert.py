#!/usr/bin/env python3
"""
Test script for security alert email template
"""

import asyncio
import random
from datetime import datetime
from email_service import EmailService

async def send_security_alert():
    """Send a realistic security alert email"""
    
    email_service = EmailService()
    
    # Realistic security alert data
    alert_data = {
        'login_location': 'Lagos, Nigeria',
        'ip_address': '197.210.84.125',
        'device_info': 'Windows 11 Desktop',
        'browser_info': 'Chrome 120.0.6099.109',
        'login_time': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'alert_time': datetime.now().strftime('%I:%M %p UTC'),
        'alert_id': f'SEC{random.randint(100000, 999999)}'
    }
    
    print("=== Sending Security Alert Email ===")
    print(f"Alert ID: {alert_data['alert_id']}")
    print(f"Location: {alert_data['login_location']}")
    print(f"IP: {alert_data['ip_address']}")
    print(f"Device: {alert_data['device_info']}")
    print(f"Time: {alert_data['login_time']}")
    print()
    
    # Send the security alert
    result = await email_service.send_email(
        to_email="ayinlasalami6@gmail.com",
        to_name="Ayinla Salami",
        subject="🔒 Security Alert: Unrecognized Login Attempt Detected",
        template_name="security_alert",
        user_id=12345,
        **alert_data
    )
    
    if result.get('success'):
        print("✅ Security alert sent successfully!")
        print(f"Message ID: {result.get('message_id', 'N/A')}")
        print("\nThe email includes:")
        print("• Professional security alert design")
        print("• Device and location information")
        print("• Action buttons for user response")
        print("• Security tips and recommendations")
        print("• Time-sensitive warning notice")
        print("• WalletSecure branding throughout")
    else:
        print("❌ Security alert failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    return result

if __name__ == '__main__':
    asyncio.run(send_security_alert())