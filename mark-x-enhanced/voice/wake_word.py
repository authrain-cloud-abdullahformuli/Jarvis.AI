"""Wake word detection for Mark-X Enhanced."""

import logging
import struct
import pvporcupine
from typing import Optional, Callable
import sounddevice as sd

from core.config import settings

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Wake word detector using Porcupine."""
    
    def __init__(self, wake_word_callback: Optional[Callable] = None):
        """Initialize wake word detector.
        
        Args:
            wake_word_callback: Function to call when wake word is detected
        """
        self.access_key = settings.porcupine_access_key
        self.wake_word_callback = wake_word_callback
        self.porcupine = None
        self.is_listening = False
        self.audio_stream = None
    
    def start(self):
        """Start listening for wake word."""
        if not self.access_key:
            logger.warning("Porcupine access key not configured")
            return
        
        if not settings.wake_word_enabled:
            logger.info("Wake word detection is disabled")
            return
        
        try:
            # Initialize Porcupine with "jarvis" wake word
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=["jarvis"]  # Built-in wake word
            )
            
            logger.info("Wake word detector initialized. Say 'Hey Jarvis' to activate.")
            self.is_listening = True
            self._listen_loop()
            
        except Exception as e:
            logger.error(f"Failed to initialize wake word detector: {e}")
            logger.info("Continuing without wake word detection")
    
    def _listen_loop(self):
        """Main listening loop for wake word detection."""
        try:
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                
                if not self.is_listening:
                    return
                
                # Convert audio data to the format Porcupine expects
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, indata)
                
                # Check for wake word
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    logger.info("Wake word detected!")
                    if self.wake_word_callback:
                        self.wake_word_callback()
            
            # Start audio stream
            self.audio_stream = sd.InputStream(
                samplerate=self.porcupine.sample_rate,
                channels=1,
                dtype='int16',
                blocksize=self.porcupine.frame_length,
                callback=audio_callback
            )
            
            self.audio_stream.start()
            logger.info("Wake word listener started")
            
        except Exception as e:
            logger.error(f"Error in wake word listening loop: {e}")
    
    def stop(self):
        """Stop listening for wake word."""
        self.is_listening = False
        
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
        
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
        
        logger.info("Wake word detector stopped")
    
    def pause(self):
        """Temporarily pause wake word detection."""
        self.is_listening = False
        logger.debug("Wake word detection paused")
    
    def resume(self):
        """Resume wake word detection."""
        self.is_listening = True
        logger.debug("Wake word detection resumed")
