"""Telegram bot integration for Mark-X Enhanced."""

import logging
import asyncio
from typing import Optional, Callable
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from core.config import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot integration for Mark-X."""
    
    def __init__(self, message_callback: Optional[Callable] = None):
        """Initialize Telegram bot.
        
        Args:
            message_callback: Async function to call with user messages
                             Should accept (text: str, user_id: str, context: dict)
        """
        self.token = settings.telegram_bot_token
        self.message_callback = message_callback
        self.application = None
        self.running = False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        await update.message.reply_text(
            "Hello sir! I'm Jarvis, your AI assistant. "
            "I can help you with various tasks. Just send me a message!"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
I can help you with:
• Opening applications
• Web searches
• Weather reports
• Sending messages
• Setting reminders
• And much more!

Just talk to me naturally, and I'll do my best to assist you, sir.
        """
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        await update.message.reply_text(
            "All systems operational, sir. Ready to assist."
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        if not update.message or not update.message.text:
            return
        
        user_text = update.message.text
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or update.effective_user.first_name
        
        logger.info(f"Received message from {username} ({user_id}): {user_text}")
        
        # Send typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # If callback is set, use it to process the message
        if self.message_callback:
            try:
                response = await self.message_callback(
                    text=user_text,
                    user_id=user_id,
                    context={
                        "platform": "telegram",
                        "username": username,
                        "chat_id": update.effective_chat.id
                    }
                )
                
                if response:
                    await update.message.reply_text(response)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await update.message.reply_text(
                    "Sorry sir, I encountered an error processing your request."
                )
        else:
            # Fallback response if no callback is set
            await update.message.reply_text(
                "I received your message, sir, but I'm not properly configured yet."
            )
    
    async def send_message(self, chat_id: str, text: str):
        """Send a message to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text to send
        """
        if self.application and self.application.bot:
            try:
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=text
                )
                logger.info(f"Sent message to chat {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send message to {chat_id}: {e}")
    
    async def send_photo(self, chat_id: str, photo_path: str, caption: Optional[str] = None):
        """Send a photo to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            photo_path: Path to photo file
            caption: Optional caption for the photo
        """
        if self.application and self.application.bot:
            try:
                with open(photo_path, 'rb') as photo:
                    await self.application.bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=caption
                    )
                logger.info(f"Sent photo to chat {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send photo to {chat_id}: {e}")
    
    async def start(self):
        """Start the Telegram bot."""
        if not self.token:
            logger.warning("Telegram bot token not configured")
            return
        
        if self.running:
            logger.warning("Telegram bot already running")
            return
        
        try:
            # Create application
            self.application = Application.builder().token(self.token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
            )
            
            # Start bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.running = True
            logger.info("Telegram bot started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            raise
    
    async def stop(self):
        """Stop the Telegram bot."""
        if self.application and self.running:
            try:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                self.running = False
                logger.info("Telegram bot stopped")
            except Exception as e:
                logger.error(f"Error stopping Telegram bot: {e}")
