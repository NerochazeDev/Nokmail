"""
Email service for sending emails via Brevo API
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = config.BREVO_API_KEY
        self.api_url = config.BREVO_API_URL
        self.rate_limit_tracker = {}
        
        if not self.api_key:
            logger.warning("Brevo API key not found in environment variables")
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        if user_id not in self.rate_limit_tracker:
            self.rate_limit_tracker[user_id] = []
        
        # Remove old entries
        self.rate_limit_tracker[user_id] = [
            timestamp for timestamp in self.rate_limit_tracker[user_id]
            if timestamp > minute_ago
        ]
        
        # Check if under limit
        if len(self.rate_limit_tracker[user_id]) >= config.EMAIL_RATE_LIMIT:
            return False
        
        # Add current timestamp
        self.rate_limit_tracker[user_id].append(now)
        return True
    
    def _load_template(self, template_name: str) -> Optional[str]:
        """Load email template from file"""
        template_path = os.path.join(config.TEMPLATES_DIR, f"{template_name}.html")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"Template {template_name} not found")
            return None
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {e}")
            return None
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available email templates"""
        templates = []
        template_info = {
            'welcome_email': 'Welcome email for new clients',
            'notification_email': 'General notification email',
            'security_alert': 'Security alert for suspicious login attempts'
        }
        
        if not os.path.exists(config.TEMPLATES_DIR):
            return templates
        
        for filename in os.listdir(config.TEMPLATES_DIR):
            if filename.endswith('.html'):
                template_name = filename[:-5]  # Remove .html extension
                description = template_info.get(template_name, 'Custom email template')
                templates.append({
                    'name': template_name,
                    'description': description
                })
        
        return templates
    
    async def send_email(self, to_email: str, to_name: str, subject: str, 
                        template_name: str, user_id: int, **template_vars) -> Dict:
        """Send email using Brevo API"""
        
        # Check rate limit
        if not self._check_rate_limit(user_id):
            return {
                'success': False,
                'error': f'Rate limit exceeded. Maximum {config.EMAIL_RATE_LIMIT} emails per minute.'
            }
        
        # Load template
        html_content = self._load_template(template_name)
        if not html_content:
            return {
                'success': False,
                'error': f'Template {template_name} not found'
            }
        
        # Replace template variables with current date and sender info
        from datetime import datetime
        template_vars.update({
            'recipient_name': to_name,
            'recipient_email': to_email,
            'current_date': datetime.now().strftime('%B %d, %Y'),
            'current_year': datetime.now().strftime('%Y'),
            'sender_email': config.DEFAULT_SENDER_EMAIL
        })
        
        for key, value in template_vars.items():
            html_content = html_content.replace(f'{{{{{key}}}}}', str(value))
        
        # Generate plain text version for better deliverability
        import re
        text_content = re.sub('<[^<]+?>', '', html_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Prepare email data with comprehensive anti-spam measures (Facebook/Gmail style)
        email_data = {
            'sender': {
                'name': config.DEFAULT_SENDER_NAME,
                'email': config.DEFAULT_SENDER_EMAIL
            },
            'to': [
                {
                    'email': to_email,
                    'name': to_name
                }
            ],
            'subject': subject,
            'htmlContent': html_content,
            'textContent': text_content,
            # Basic legitimate headers only
            'headers': {
                'Reply-To': config.DEFAULT_SENDER_EMAIL
            },
            # Add tracking and deliverability settings
            'params': {
                'FNAME': to_name.split(' ')[0] if ' ' in to_name else to_name,
                'LNAME': to_name.split(' ')[-1] if ' ' in to_name else '',
                'EMAIL': to_email
            },
            # Enable tracking for better sender reputation  
            'tags': ['account-access', 'notification']
        }
        
        # Send email
        try:
            headers = {
                'accept': 'application/json',
                'api-key': self.api_key,
                'content-type': 'application/json'
            }
            
            response = requests.post(
                self.api_url,
                json=email_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                # Log successful email
                self._log_email(user_id, to_email, to_name, subject, template_name, True)
                return {
                    'success': True,
                    'message_id': response.json().get('messageId')
                }
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                logger.error(f"Brevo API error: {error_msg}")
                self._log_email(user_id, to_email, to_name, subject, template_name, False, error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"Email sending failed: {error_msg}")
            self._log_email(user_id, to_email, to_name, subject, template_name, False, error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Email sending failed: {error_msg}")
            self._log_email(user_id, to_email, to_name, subject, template_name, False, error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def _log_email(self, user_id: int, to_email: str, to_name: str, 
                   subject: str, template: str, success: bool, error: str = None):
        """Log email sending attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'to_email': to_email,
            'to_name': to_name,
            'subject': subject,
            'template': template,
            'success': success,
            'error': error
        }
        
        try:
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
            # Load existing logs
            logs = []
            if os.path.exists(config.EMAIL_LOG_FILE):
                try:
                    with open(config.EMAIL_LOG_FILE, 'r') as file:
                        logs = json.load(file)
                except json.JSONDecodeError:
                    logs = []
            
            # Add new log entry
            logs.append(log_entry)
            
            # Keep only last 1000 entries to prevent file from growing too large
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Save logs
            with open(config.EMAIL_LOG_FILE, 'w') as file:
                json.dump(logs, file, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log email: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get email statistics for a user"""
        stats = {
            'total_sent': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'last_email_date': None
        }
        
        try:
            if not os.path.exists(config.EMAIL_LOG_FILE):
                return stats
            
            with open(config.EMAIL_LOG_FILE, 'r') as file:
                logs = json.load(file)
            
            user_logs = [log for log in logs if log.get('user_id') == user_id]
            
            stats['total_sent'] = len(user_logs)
            stats['successful_sends'] = len([log for log in user_logs if log.get('success')])
            stats['failed_sends'] = stats['total_sent'] - stats['successful_sends']
            
            if user_logs:
                # Get most recent email date
                latest_log = max(user_logs, key=lambda x: x.get('timestamp', ''))
                stats['last_email_date'] = latest_log.get('timestamp', '').split('T')[0]
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
        
        return stats
