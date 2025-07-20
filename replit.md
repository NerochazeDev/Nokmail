# Telegram Email Bot Project

## Overview
This project is a Telegram bot that sends security alert emails to users. The bot simulates wallet security notifications by sending professional-looking email alerts about suspicious login attempts.

## Recent Changes
**July 20, 2025:**
- ✓ Fixed duplicate email issue by removing redundant "Web Telegram Bot" workflow
- ✓ Added duplicate email prevention mechanism to EmailService
- ✓ Implemented 30-second time window to prevent identical emails to same recipient
- ✓ Only "Working Telegram Bot" workflow is now active to prevent conflicts

## Project Architecture

### Core Components
1. **EmailService** (`email_service.py`) - Handles email sending via Brevo API
2. **Telegram Bots**:
   - `simple_main.py` - Main bot implementation (currently active)
   - `web_bot.py` - Web-enabled bot (disabled to prevent duplicates)
   - `telegram_bot.py` - Advanced bot with client management (has import issues)

### Key Features
- Security alert email templates
- Rate limiting (10 emails per minute per user)
- Duplicate prevention (30-second window)
- Email logging and statistics
- Multiple email templates support

### Workflow Configuration
- **Working Telegram Bot**: `python simple_main.py` (Active)
- **Telegram Email Bot**: Failed due to import errors
- **telegram_bot_setup**: Package installation (Completed)

## User Preferences
- User language: English
- Issue focus: Preventing duplicate emails
- Communication style: Simple, non-technical explanations

## Recent Issues Resolved
- **Multiple Email Problem**: Root cause was two bot instances running simultaneously, both processing the same Telegram messages and sending duplicate emails
- **Solution**: Removed duplicate workflow and added duplicate detection logic

## Current Status
- ✅ Bot is running and functional
- ✅ Duplicate email prevention implemented
- ✅ Only one bot instance active
- ⚠️ Monitoring for any remaining duplicate issues