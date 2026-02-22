# Mark-X Enhanced - Quick Reference

## 🚀 Quick Commands

### Setup
```bash
./setup.sh                    # Automated setup
cp .env.example .env          # Create config
python main.py                # Start application
```

### Development
```bash
source venv/bin/activate      # Activate virtual env
pip install -r requirements.txt  # Install deps
tail -f mark_x.log           # View logs
rm data/jarvis.db            # Reset database
```

## 🔑 API Keys You Need

| Service | Required? | Get It From | Purpose |
|---------|-----------|-------------|---------|
| OpenRouter | ✅ Yes | https://openrouter.ai | LLM processing |
| Telegram | Optional | @BotFather | Telegram bot |
| Discord | Optional | discord.com/developers | Discord bot |
| ElevenLabs | Optional | elevenlabs.io | Voice synthesis |
| Porcupine | Optional | picovoice.ai | Wake word |

## 📁 Project Structure

```
mark-x-enhanced/
├── main.py              # ← Start here
├── .env                 # ← Add your keys here
├── core/
│   ├── config.py        # Settings
│   ├── agent_orchestrator.py  # Main brain
│   ├── skills_loader.py       # Skill manager
│   └── scheduler.py           # Task scheduler
├── skills/
│   ├── base_skill.py    # Skill template
│   └── *.py            # ← Add skills here
├── integrations/
│   ├── telegram_bot.py  # Telegram
│   └── discord_bot.py   # Discord
└── memory/
    └── persistent_db.py # Database
```

## 🎨 Create a Skill (Template)

```python
from typing import Dict, Any, List
from skills.base_skill import (
    BaseSkill, SkillCategory, 
    SkillParameter, SkillResult
)

class MySkill(BaseSkill):
    def get_name(self) -> str:
        return "my_skill"
    
    def get_description(self) -> str:
        return "What this skill does"
    
    def get_category(self) -> SkillCategory:
        return SkillCategory.AUTOMATION
    
    def get_parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="param",
                description="Param description",
                required=True
            )
        ]
    
    def get_examples(self) -> List[str]:
        return ["example command"]
    
    async def execute(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> SkillResult:
        # Your logic here
        return SkillResult(
            success=True,
            message="Done, sir!"
        )
```

## 🔧 Configuration (.env)

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...

# Platform (pick at least one)
TELEGRAM_BOT_TOKEN=123456:ABC...
DISCORD_BOT_TOKEN=MTA...

# Optional
ELEVENLABS_API_KEY=...
VOSK_MODEL_PATH=/path/to/model
PORCUPINE_ACCESS_KEY=...
WAKE_WORD_ENABLED=true
DEBUG=false
```

## 💬 Example Commands

### Telegram/Discord
```
/start
/help
/status
Open Chrome
Tell me a joke
What can you do?
```

## 🐛 Debugging

### Check Logs
```bash
tail -n 50 mark_x.log         # Last 50 lines
tail -f mark_x.log            # Follow logs
grep ERROR mark_x.log         # Find errors
```

### Test Components
```bash
# Test Python
python --version

# Test sounddevice
python -m sounddevice

# Test OpenRouter
curl https://openrouter.ai/api/v1/models
```

### Common Issues

**Bot not responding?**
```bash
# 1. Check API keys
cat .env | grep TOKEN

# 2. Check logs
tail mark_x.log

# 3. Restart
pkill -f main.py && python main.py
```

**Module not found?**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Database error?**
```bash
rm data/jarvis.db
python main.py
```

## 📊 Database Tables

- `conversations` - Chat history
- `user_memory` - User facts
- `scheduled_tasks` - Cron jobs
- `skill_executions` - Logs

## 🎯 Skill Categories

```python
SkillCategory.SYSTEM          # OS operations
SkillCategory.COMMUNICATION   # Messaging
SkillCategory.INFORMATION     # Data retrieval
SkillCategory.AUTOMATION      # Workflows
SkillCategory.ENTERTAINMENT   # Fun stuff
SkillCategory.PRODUCTIVITY    # Work tools
```

## 🔗 Useful URLs

- **OpenRouter**: https://openrouter.ai
- **Telegram BotFather**: https://t.me/botfather
- **Discord Developers**: https://discord.com/developers
- **Vosk Models**: https://alphacephei.com/vosk/models
- **Porcupine**: https://picovoice.ai

## 📞 Get Help

1. Check `mark_x.log`
2. Review `.env` configuration
3. Read `GETTING_STARTED.md`
4. Study example skills
5. Test components individually

## ⚡ Pro Tips

- Start with Telegram (easiest)
- Test skills individually
- Use DEBUG=true for development
- Keep API keys secret
- Create simple skills first
- Check logs frequently

## 🎓 Learning Path

1. **Read**: README.md
2. **Setup**: ./setup.sh
3. **Test**: Send messages to bot
4. **Study**: skills/open_app_skill.py
5. **Create**: Your first skill
6. **Build**: Something amazing!

## 📝 Cheat Sheet

```bash
# Essential Commands
./setup.sh                    # First-time setup
python main.py               # Start
Ctrl+C                       # Stop
tail -f mark_x.log          # Watch logs
rm data/jarvis.db           # Reset DB

# Skill Development
1. Copy skills/open_app_skill.py
2. Modify for your needs
3. Save as skills/my_skill.py
4. Restart application
5. Test!

# Environment
source venv/bin/activate     # Activate
deactivate                   # Deactivate
pip freeze                   # List packages
```

---

**Need more details?** See README.md or GETTING_STARTED.md

**Ready to build?** Create your first skill in `skills/`!
