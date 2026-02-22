"""Discord bot integration for Mark-X Enhanced."""

import logging
import discord
from typing import Optional, Callable
from discord.ext import commands

from core.config import settings

logger = logging.getLogger(__name__)


class DiscordBot:
    """Discord bot integration for Mark-X."""
    
    def __init__(self, message_callback: Optional[Callable] = None):
        """Initialize Discord bot.
        
        Args:
            message_callback: Async function to call with user messages
        """
        self.token = settings.discord_bot_token
        self.message_callback = message_callback
        self.bot = None
        self.running = False
    
    def create_bot(self):
        """Create and configure the Discord bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        
        bot = commands.Bot(command_prefix="!", intents=intents)
        
        @bot.event
        async def on_ready():
            logger.info(f"Discord bot logged in as {bot.user}")
            self.running = True
        
        @bot.event
        async def on_message(message):
            # Ignore messages from the bot itself
            if message.author == bot.user:
                return
            
            # Check if bot is mentioned or in DM
            is_mentioned = bot.user in message.mentions
            is_dm = isinstance(message.channel, discord.DMChannel)
            
            if is_mentioned or is_dm:
                user_text = message.content.replace(f'<@{bot.user.id}>', '').strip()
                user_id = str(message.author.id)
                username = message.author.name
                
                logger.info(f"Received message from {username} ({user_id}): {user_text}")
                
                # Show typing indicator
                async with message.channel.typing():
                    if self.message_callback:
                        try:
                            response = await self.message_callback(
                                text=user_text,
                                user_id=user_id,
                                context={
                                    "platform": "discord",
                                    "username": username,
                                    "channel_id": message.channel.id
                                }
                            )
                            
                            if response:
                                await message.reply(response)
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            await message.reply(
                                "Sorry sir, I encountered an error processing your request."
                            )
                    else:
                        await message.reply(
                            "I received your message, sir, but I'm not properly configured yet."
                        )
            
            # Process commands
            await bot.process_commands(message)
        
        @bot.command(name="help")
        async def help_command(ctx):
            """Help command."""
            help_text = """
**Jarvis - Your AI Assistant**

I can help you with:
• Opening applications
• Web searches
• Weather reports
• Setting reminders
• And much more!

Just mention me or DM me, and I'll do my best to assist you, sir.
            """
            await ctx.send(help_text)
        
        @bot.command(name="status")
        async def status_command(ctx):
            """Status command."""
            await ctx.send("All systems operational, sir. Ready to assist.")
        
        return bot
    
    async def send_message(self, channel_id: int, text: str):
        """Send a message to a Discord channel.
        
        Args:
            channel_id: Discord channel ID
            text: Message text to send
        """
        if self.bot:
            try:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send(text)
                    logger.info(f"Sent message to channel {channel_id}")
            except Exception as e:
                logger.error(f"Failed to send message to {channel_id}: {e}")
    
    async def start(self):
        """Start the Discord bot."""
        if not self.token:
            logger.warning("Discord bot token not configured")
            return
        
        if self.running:
            logger.warning("Discord bot already running")
            return
        
        try:
            self.bot = self.create_bot()
            await self.bot.start(self.token)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            raise
    
    async def stop(self):
        """Stop the Discord bot."""
        if self.bot and self.running:
            try:
                await self.bot.close()
                self.running = False
                logger.info("Discord bot stopped")
            except Exception as e:
                logger.error(f"Error stopping Discord bot: {e}")
