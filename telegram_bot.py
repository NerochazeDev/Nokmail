"""
Telegram Bot implementation for email management
"""

import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from email_service import EmailService
from client_manager import ClientManager
import config

logger = logging.getLogger(__name__)

class TelegramEmailBot:
    def __init__(self, token):
        self.token = token
        self.email_service = EmailService()
        self.client_manager = ClientManager()
        self.application = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("add_client", self.add_client_command))
        self.application.add_handler(CommandHandler("list_clients", self.list_clients_command))
        self.application.add_handler(CommandHandler("remove_client", self.remove_client_command))
        self.application.add_handler(CommandHandler("send_email", self.send_email_command))
        self.application.add_handler(CommandHandler("templates", self.templates_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Message handler for general messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_message = f"""
🤖 *Welcome to Email Bot, {user.first_name}!*

I can help you manage your clients and send emails using the Brevo API.

*Available Commands:*
• `/help` - Show detailed help
• `/add_client` - Add a new client
• `/list_clients` - Show your clients
• `/send_email` - Send an email
• `/templates` - View email templates
• `/stats` - View email statistics

Get started by adding your first client with `/add_client`!
        """
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 *Email Bot Help*

*Client Management:*
• `/add_client <name> <email>` - Add a new client
  Example: `/add_client John Doe john@example.com`

• `/list_clients` - Show all your clients with IDs

• `/remove_client <client_id>` - Remove a client
  Example: `/remove_client 1`

*Email Operations:*
• `/send_email <client_id> <template> <subject>` - Send email
  Example: `/send_email 1 welcome "Welcome to our service"`

• `/templates` - View available email templates

• `/stats` - View your email sending statistics

*Notes:*
• Each user can manage up to {config.MAX_CLIENTS_PER_USER} clients
• Email sending is rate-limited to {config.EMAIL_RATE_LIMIT} emails per minute
• All emails are logged for tracking
        """.format(
            config.MAX_CLIENTS_PER_USER,
            config.EMAIL_RATE_LIMIT
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def add_client_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add_client command"""
        user_id = update.effective_user.id
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Usage: `/add_client <name> <email>`\n"
                "Example: `/add_client John Doe john@example.com`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Parse arguments (name can have spaces, email is last)
        email = context.args[-1]
        name = " ".join(context.args[:-1])
        
        try:
            client_id = self.client_manager.add_client(user_id, name, email)
            await update.message.reply_text(
                f"✅ Client added successfully!\n"
                f"*Name:* {name}\n"
                f"*Email:* {email}\n"
                f"*Client ID:* {client_id}",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error adding client: {str(e)}")
    
    async def list_clients_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list_clients command"""
        user_id = update.effective_user.id
        
        try:
            clients = self.client_manager.get_user_clients(user_id)
            
            if not clients:
                await update.message.reply_text("📭 You don't have any clients yet. Use `/add_client` to add one!")
                return
            
            message = "👥 *Your Clients:*\n\n"
            for client in clients:
                message += f"*ID:* {client['id']}\n"
                message += f"*Name:* {client['name']}\n"
                message += f"*Email:* {client['email']}\n"
                message += f"*Added:* {client['created_at']}\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error retrieving clients: {str(e)}")
    
    async def remove_client_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remove_client command"""
        user_id = update.effective_user.id
        
        if len(context.args) != 1:
            await update.message.reply_text(
                "❌ Usage: `/remove_client <client_id>`\n"
                "Example: `/remove_client 1`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            client_id = int(context.args[0])
            removed_client = self.client_manager.remove_client(user_id, client_id)
            
            await update.message.reply_text(
                f"✅ Client removed successfully!\n"
                f"*Name:* {removed_client['name']}\n"
                f"*Email:* {removed_client['email']}",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except ValueError:
            await update.message.reply_text("❌ Client ID must be a number")
        except Exception as e:
            await update.message.reply_text(f"❌ Error removing client: {str(e)}")
    
    async def send_email_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /send_email command"""
        user_id = update.effective_user.id
        
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ Usage: `/send_email <client_id> <template> <subject>`\n"
                "Example: `/send_email 1 welcome \"Welcome to our service\"`\n"
                "Use `/templates` to see available templates",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            client_id = int(context.args[0])
            template_name = context.args[1]
            subject = " ".join(context.args[2:])
            
            # Get client info
            client = self.client_manager.get_client(user_id, client_id)
            if not client:
                await update.message.reply_text("❌ Client not found")
                return
            
            # Send email
            result = await self.email_service.send_email(
                to_email=client['email'],
                to_name=client['name'],
                subject=subject,
                template_name=template_name,
                user_id=user_id
            )
            
            if result['success']:
                await update.message.reply_text(
                    f"✅ Email sent successfully!\n"
                    f"*To:* {client['name']} ({client['email']})\n"
                    f"*Subject:* {subject}\n"
                    f"*Template:* {template_name}",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(f"❌ Failed to send email: {result['error']}")
                
        except ValueError:
            await update.message.reply_text("❌ Client ID must be a number")
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending email: {str(e)}")
    
    async def templates_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /templates command"""
        templates = self.email_service.get_available_templates()
        
        if not templates:
            await update.message.reply_text("❌ No email templates available")
            return
        
        message = "📧 *Available Email Templates:*\n\n"
        for template in templates:
            message += f"• `{template['name']}` - {template['description']}\n"
        
        message += "\nUse template name in `/send_email` command"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        
        try:
            stats = self.email_service.get_user_stats(user_id)
            client_count = len(self.client_manager.get_user_clients(user_id))
            
            message = f"""
📊 *Your Statistics:*

*Clients:* {client_count}/{config.MAX_CLIENTS_PER_USER}
*Total Emails Sent:* {stats['total_sent']}
*Successful Sends:* {stats['successful_sends']}
*Failed Sends:* {stats['failed_sends']}
*Last Email:* {stats['last_email_date'] or 'Never'}

*Rate Limit:* {config.EMAIL_RATE_LIMIT} emails/minute
            """
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error retrieving stats: {str(e)}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle non-command messages"""
        await update.message.reply_text(
            "👋 Hi! I'm an email bot. Use `/help` to see what I can do for you!"
        )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.message:
            await update.message.reply_text(
                "❌ An error occurred while processing your request. Please try again."
            )
    
    def run(self):
        """Start the bot"""
        # Add error handler
        self.application.add_error_handler(self.error_handler)
        
        # Set bot commands for UI
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help message"),
            BotCommand("add_client", "Add a new client"),
            BotCommand("list_clients", "List your clients"),
            BotCommand("send_email", "Send an email"),
            BotCommand("templates", "View email templates"),
            BotCommand("stats", "View statistics")
        ]
        
        # Run the bot
        logger.info("Bot is starting...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
