#!/usr/bin/env python3
"""
WalletSecure Security Alert System
Professional tool for sending security warnings
"""

import asyncio
import random
from datetime import datetime
from email_service import EmailService
from client_manager import ClientManager

class SecurityAlertSystem:
    def __init__(self):
        self.email_service = EmailService()
        self.client_manager = ClientManager()
    
    async def send_login_warning(self, email: str, name: str = None, location: str = None, 
                                ip: str = None, device: str = None, browser: str = None):
        """Send a professional security alert for suspicious login"""
        
        if not name:
            name = email.split('@')[0].title()
        
        # Generate realistic data if not provided
        locations = ['Lagos, Nigeria', 'Abuja, Nigeria', 'Port Harcourt, Nigeria', 
                    'Kano, Nigeria', 'Ibadan, Nigeria', 'Unknown Location']
        devices = ['Windows 11 Desktop', 'MacBook Pro', 'iPhone 15', 'Android Phone', 
                  'iPad', 'Linux Ubuntu', 'Unknown Device']
        browsers = ['Chrome 120.0.6099.109', 'Safari 17.2.1', 'Firefox 121.0', 
                   'Edge 120.0.2210.77', 'Mobile Safari', 'Chrome Mobile']
        
        alert_data = {
            'login_location': location or random.choice(locations),
            'ip_address': ip or f"{random.randint(100,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'device_info': device or random.choice(devices),
            'browser_info': browser or random.choice(browsers),
            'login_time': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'alert_time': datetime.now().strftime('%I:%M %p UTC'),
            'alert_id': f'WS{random.randint(100000, 999999)}'
        }
        
        # Send the security alert
        result = await self.email_service.send_email(
            to_email=email,
            to_name=name,
            subject="🔒 URGENT: Unrecognized Login Attempt to Your Wallet",
            template_name="security_alert",
            user_id=99999,  # Security system user ID
            **alert_data
        )
        
        return {
            'success': result.get('success', False),
            'message_id': result.get('message_id'),
            'error': result.get('error'),
            'alert_id': alert_data['alert_id'],
            'details': alert_data
        }
    
    def get_all_clients(self):
        """Get all clients for mass security alerts"""
        return self.client_manager.get_total_clients()

async def demo_security_system():
    """Demonstrate the security alert system"""
    print("🔒 WalletSecure Security Alert System")
    print("=" * 50)
    
    security_system = SecurityAlertSystem()
    
    # Send alert to your email
    print("Sending security alert...")
    result = await security_system.send_login_warning(
        email="ayinlasalami6@gmail.com",
        name="Ayinla Salami",
        location="Lagos, Nigeria",
        device="Unknown Windows Device"
    )
    
    if result['success']:
        print(f"✅ Security alert sent successfully!")
        print(f"   Alert ID: {result['alert_id']}")
        print(f"   Message ID: {result['message_id']}")
        print(f"   Location: {result['details']['login_location']}")
        print(f"   IP Address: {result['details']['ip_address']}")
        print(f"   Device: {result['details']['device_info']}")
        print()
        print("📧 Check your email for the professional security alert!")
        print("   Features included:")
        print("   • Gradient header with security icons")
        print("   • Device and location details")
        print("   • Action buttons (Secure Account / This Was Me)")
        print("   • Security tips and recommendations")
        print("   • 24-hour time limit warning")
        print("   • Professional WalletSecure branding")
    else:
        print(f"❌ Alert failed: {result['error']}")

if __name__ == '__main__':
    asyncio.run(demo_security_system())