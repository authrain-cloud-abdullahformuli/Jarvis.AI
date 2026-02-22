"""
Mark-X Enhanced - Voice-Activated AI Assistant
Main entry point for the application
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import settings
from core.agent_orchestrator import orchestrator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mark_x.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MarkXEnhanced:
    """Main application class."""
    
    def __init__(self):
        self.running = False
    
    async def start(self):
        """Start the application."""
        logger.info("=" * 60)
        logger.info("Mark-X Enhanced - Voice-Activated AI Assistant")
        logger.info("=" * 60)
        
        # Initialize orchestrator
        await orchestrator.initialize()
        
        # Start all services
        await orchestrator.start()
        
        self.running = True
        logger.info("Mark-X Enhanced is now running!")
        logger.info("Press Ctrl+C to stop")
        
        # Keep running
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        """Stop the application."""
        logger.info("Shutting down Mark-X Enhanced...")
        self.running = False
        await orchestrator.stop()
        logger.info("Goodbye, sir!")


async def main():
    """Main entry point."""
    app = MarkXEnhanced()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        asyncio.create_task(app.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await app.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
