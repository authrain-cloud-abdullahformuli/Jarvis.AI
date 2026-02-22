# 🤖 Mark-X Enhanced - Voice-Activated AI Assistant

A powerful, extensible AI assistant that combines voice interaction with multi-platform messaging integration. Built to compete with OpenClaw while maintaining a **voice-first, privacy-focused** approach.

## 🌟 Features

### Core Capabilities
- ✅ **Voice-First Design** - Natural voice interaction with wake word detection
- ✅ **Multi-Platform Integration** - Telegram, Discord, and more
- ✅ **Persistent Memory** - SQLite-based long-term memory with vector embeddings
- ✅ **Dynamic Skills System** - Easy-to-extend plugin architecture
- ✅ **Task Scheduling** - Cron-like scheduler for automated tasks and reminders
- ✅ **Background Execution** - Async task queue for long-running operations
- ✅ **Proactive Features** - Scheduled reminders and autonomous workflows
- ✅ **Web API** - REST API for programmatic control (coming soon)
- ✅ **100% Local** - Privacy-focused, runs entirely on your machine

### Key Differentiators vs OpenClaw
1. **Voice-Native** - Built for voice interaction from the ground up
2. **Local-First** - No cloud dependencies, complete privacy
3. **Visual Feedback** - Animated assistant interface
4. **Cross-Platform** - Desktop voice + mobile text
5. **Lightweight** - Fast startup, minimal dependencies

## 📋 Prerequisites

- Python 3.9 or higher
- macOS, Linux, or Windows
- Microphone (for voice features)
- Internet connection (for LLM API calls)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd mark-x-enhanced
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional but recommended
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
PORCUPINE_ACCESS_KEY=your_porcupine_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DISCORD_BOT_TOKEN=your_discord_bot_token
```

### 3. Download Vosk Model (for voice recognition)

Download a Vosk model from https://alphacephei.com/vosk/models

```bash
# Example for English (small model)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

Update `.env`:
```bash
VOSK_MODEL_PATH=/path/to/vosk-model-small-en-us-0.15
```

### 4. Run the Application

```bash
python main.py
```

## 🎯 Usage

### Text Mode (Telegram/Discord)

1. **Telegram**: 
   - Create a bot via [@BotFather](https://t.me/botfather)
   - Add token to `.env`
   - Start the bot and send messages

2. **Discord**:
   - Create a bot in [Discord Developer Portal](https://discord.com/developers/applications)
   - Add token to `.env`
   - Invite bot to your server and mention it

### Voice Mode

If wake word is enabled:
1. Say "Hey Jarvis" to activate
2. Speak your command
3. Wait for response

### Example Commands

```
"Open Chrome"
"What's the weather in London?"
"Remind me to call John at 3 PM"
"Search for Python tutorials"
"Tell me about my schedule"
```

## 🎨 Creating Custom Skills

Skills are the heart of Mark-X Enhanced. Here's how to create one:

### Step 1: Create a Skill File

Create `skills/my_custom_skill.py`:

```python
from typing import Dict, Any, List
from skills.base_skill import BaseSkill, SkillCategory, SkillParameter, SkillResult


class MyCustomSkill(BaseSkill):
    """Description of what your skill does."""
    
    def get_name(self) -> str:
        return "my_custom_skill"
    
    def get_description(self) -> str:
        return "Brief description for the LLM to understand when to use this skill"
    
    def get_category(self) -> SkillCategory:
        return SkillCategory.AUTOMATION  # or SYSTEM, COMMUNICATION, etc.
    
    def get_parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="param1",
                description="What this parameter represents",
                required=True,
                param_type=str
            )
        ]
    
    def get_examples(self) -> List[str]:
        return [
            "example command 1",
            "example command 2"
        ]
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
        """Execute your skill logic here."""
        param1 = parameters.get("param1")
        
        try:
            # Your logic here
            result_data = {"output": "something"}
            
            return SkillResult(
                success=True,
                message="Skill executed successfully, sir.",
                data=result_data
            )
        except Exception as e:
            return SkillResult(
                success=False,
                message=f"An error occurred: {str(e)}"
            )
```

### Step 2: Restart the Application

Skills are auto-discovered on startup. No registration needed!

## 🛠️ Architecture

```
mark-x-enhanced/
├── main.py                    # Entry point
├── core/
│   ├── config.py              # Configuration management
│   ├── agent_orchestrator.py # Central coordinator
│   ├── skills_loader.py       # Dynamic skill loading
│   ├── scheduler.py           # Task scheduling
│   └── task_queue.py          # Background tasks
├── memory/
│   ├── persistent_db.py       # SQLite database
│   ├── vector_store.py        # Semantic memory
│   └── memory_manager.py      # Memory operations
├── skills/
│   ├── base_skill.py          # Skill interface
│   ├── open_app_skill.py      # Example skill
│   └── [your_skills].py       # Add more here!
├── integrations/
│   ├── telegram_bot.py        # Telegram integration
│   ├── discord_bot.py         # Discord integration
│   ├── whatsapp_handler.py    # WhatsApp (future)
│   └── webhook_server.py      # Webhook handler
├── voice/
│   ├── speech_to_text.py      # Voice recognition
│   ├── text_to_speech.py      # Voice synthesis
│   └── wake_word.py           # Wake word detection
└── web/
    ├── api.py                 # REST API
    └── frontend/              # Web dashboard
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for LLM |
| `ELEVENLABS_API_KEY` | No | ElevenLabs for voice synthesis |
| `VOSK_MODEL_PATH` | For voice | Path to Vosk model |
| `PORCUPINE_ACCESS_KEY` | For wake word | Porcupine API key |
| `TELEGRAM_BOT_TOKEN` | For Telegram | Bot token from BotFather |
| `DISCORD_BOT_TOKEN` | For Discord | Bot token from Discord |
| `WAKE_WORD_ENABLED` | No | Enable/disable wake word (default: true) |
| `SCHEDULER_ENABLED` | No | Enable task scheduler (default: true) |
| `DEBUG` | No | Enable debug mode (default: false) |

### Getting API Keys

1. **OpenRouter** (Required):
   - Sign up at https://openrouter.ai
   - Get API key from dashboard
   - Free tier available

2. **ElevenLabs** (Optional, for better voice):
   - Sign up at https://elevenlabs.io
   - Free tier: 10,000 characters/month
   - Alternative: Use system TTS

3. **Porcupine** (Optional, for wake word):
   - Sign up at https://picovoice.ai
   - Free tier available
   - Get access key from console

4. **Telegram Bot** (Optional):
   - Message [@BotFather](https://t.me/botfather)
   - Use `/newbot` command
   - Copy the token

5. **Discord Bot** (Optional):
   - Visit https://discord.com/developers/applications
   - Create new application
   - Add bot and copy token

## 📊 Database Schema

The system uses SQLite with the following tables:

- **conversations** - Full conversation history
- **user_memory** - Long-term user preferences and facts
- **scheduled_tasks** - Cron jobs and reminders
- **skill_executions** - Execution logs and analytics

## 🚧 Roadmap

### Phase 1: MVP ✅ (Complete)
- [x] Core skills system
- [x] Persistent memory (SQLite)
- [x] Telegram integration
- [x] Task scheduler
- [x] Discord integration

### Phase 2: Advanced Features (In Progress)
- [ ] Wake word detection (Porcupine integrated, needs testing)
- [ ] Vector embeddings for semantic memory
- [ ] FastAPI web dashboard
- [ ] Webhook server for external events
- [ ] More built-in skills (weather, web search, etc.)

### Phase 3: Polish (Coming Soon)
- [ ] Voice UI with animated face
- [ ] WhatsApp integration
- [ ] Mobile app companion
- [ ] Skill marketplace
- [ ] Cloud sync (optional)

## 🤝 Contributing

Want to add skills or features?

1. Fork the repository
2. Create a feature branch
3. Add your skill in `skills/`
4. Test it thoroughly
5. Submit a pull request

## 📝 License

For educational and personal use. See original Mark-X license.

## 🙏 Credits

- Original Mark-X by FatihMakes
- Inspired by OpenClaw's architecture
- Built with ❤️ to be better than both

## 🆘 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Voice recognition not working
- Check microphone permissions
- Verify Vosk model path in `.env`
- Test with: `python -m sounddevice`

### Bot not responding
- Verify API keys in `.env`
- Check logs in `mark_x.log`
- Ensure bots have proper permissions

### Database errors
- Delete `data/jarvis.db` to reset
- Check write permissions in `data/` folder

## 📞 Support

For issues, questions, or contributions:
- Check the logs: `mark_x.log`
- Review configuration: `.env`
- Test individual components

---

**Built to compete, designed to win. Mark-X Enhanced - Your voice-activated future, today.** 🚀
