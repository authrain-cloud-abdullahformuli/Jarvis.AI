# Getting Started with Mark-X Enhanced

This guide will help you get Mark-X Enhanced up and running quickly.

## Installation (5 minutes)

### Option 1: Automated Setup (Recommended)

```bash
cd mark-x-enhanced
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create `.env` file from template
- Set up data directory

### Option 2: Manual Setup

```bash
cd mark-x-enhanced
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
mkdir -p data
```

## Configuration (10 minutes)

### Step 1: Get OpenRouter API Key (Required)

1. Go to https://openrouter.ai
2. Sign up for a free account
3. Navigate to "Keys" section
4. Create a new API key
5. Copy the key

Add to `.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Step 2: Choose Your Interface

#### Option A: Telegram Bot (Easiest)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to create your bot
4. Copy the token (looks like: `123456:ABC-DEF1234...`)
5. Add to `.env`:
```bash
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=your_chat_id  # Optional, get from @userinfobot
```

#### Option B: Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Go to "Bot" section
4. Click "Add Bot"
5. Under "Token", click "Copy"
6. Enable "Message Content Intent"
7. Add to `.env`:
```bash
DISCORD_BOT_TOKEN=your-discord-bot-token-here
```

8. Invite bot to your server:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot
```

#### Option C: Voice Mode (Advanced)

1. Download Vosk model:
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

2. Add to `.env`:
```bash
VOSK_MODEL_PATH=/path/to/vosk-model-small-en-us-0.15
```

3. Optional: Get Porcupine key for wake word:
   - Sign up at https://picovoice.ai
   - Get access key from console
   - Add to `.env`:
```bash
PORCUPINE_ACCESS_KEY=your-porcupine-key-here
```

## First Run (2 minutes)

### Start the Application

```bash
source venv/bin/activate  # Activate virtual environment
python main.py
```

You should see:
```
============================================================
Mark-X Enhanced - Voice-Activated AI Assistant
============================================================
Initializing Agent Orchestrator...
Loaded 1 skills
Task scheduler started
Telegram bot started successfully
Mark-X Enhanced is now running!
Press Ctrl+C to stop
```

## Testing Your Setup

### Test 1: Telegram Bot

1. Open Telegram
2. Find your bot
3. Send: `/start`
4. You should get: "Hello sir! I'm Jarvis..."
5. Try: "Open Chrome"

### Test 2: Discord Bot

1. Open Discord
2. Mention your bot: `@YourBot hello`
3. You should get a response
4. Try: `@YourBot what can you do?`

### Test 3: Check Logs

```bash
tail -f mark_x.log
```

You should see activity logs when interacting with the bot.

## Your First Custom Skill (5 minutes)

Let's create a "joke" skill:

### 1. Create the Skill File

Create `skills/joke_skill.py`:

```python
import random
from typing import Dict, Any, List
from skills.base_skill import BaseSkill, SkillCategory, SkillParameter, SkillResult


class JokeSkill(BaseSkill):
    """Tells jokes to the user."""
    
    def get_name(self) -> str:
        return "tell_joke"
    
    def get_description(self) -> str:
        return "Tells a random joke to make the user laugh"
    
    def get_category(self) -> SkillCategory:
        return SkillCategory.ENTERTAINMENT
    
    def get_parameters(self) -> List[SkillParameter]:
        return []  # No parameters needed
    
    def get_examples(self) -> List[str]:
        return [
            "tell me a joke",
            "make me laugh",
            "I need a joke",
            "say something funny"
        ]
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!"
        ]
        
        joke = random.choice(jokes)
        
        return SkillResult(
            success=True,
            message=joke,
            data={"joke": joke}
        )
```

### 2. Restart the Application

```bash
# Press Ctrl+C to stop
# Then start again
python main.py
```

You should see:
```
Loaded 2 skills
```

### 3. Test Your Skill

Send to your bot: "Tell me a joke"

You should get one of the jokes!

## Common Workflows

### 1. Opening Applications

"Open Chrome"
"Launch Spotify"
"Start calculator"

### 2. Setting Reminders (Coming Soon)

"Remind me to call John at 3 PM"
"Set a reminder for tomorrow at 9 AM"

### 3. Conversational Memory

The bot remembers your conversations:
- "My name is Alex"
- Later: "What's my name?" → "Your name is Alex, sir"

## Troubleshooting

### Bot doesn't respond

**Check 1: API Keys**
```bash
cat .env | grep API_KEY
```
Make sure your keys are present.

**Check 2: Logs**
```bash
tail -n 50 mark_x.log
```
Look for errors.

**Check 3: Network**
```bash
curl https://openrouter.ai/api/v1/models
```
Should return JSON response.

### "Module not found" Error

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Database Errors

```bash
rm data/jarvis.db
python main.py
```
This will recreate the database.

## Next Steps

### Learn More
- Read `README.md` for full documentation
- Explore existing skills in `skills/` directory
- Check out the architecture in `core/`

### Add More Skills
- Weather reports
- Web search
- Calendar integration
- Email sending
- System commands

### Contribute
- Share your skills
- Report bugs
- Suggest features

## Quick Reference

### Project Structure
```
mark-x-enhanced/
├── main.py              # Start here
├── .env                 # Your configuration
├── skills/              # Add skills here
│   ├── base_skill.py
│   └── your_skill.py
├── data/                # Database & storage
└── mark_x.log          # Check logs here
```

### Key Commands
```bash
# Start
python main.py

# Stop
Ctrl+C

# View logs
tail -f mark_x.log

# Reset database
rm data/jarvis.db
```

### Environment Variables
```bash
# Required
OPENROUTER_API_KEY=...

# Optional
TELEGRAM_BOT_TOKEN=...
DISCORD_BOT_TOKEN=...
VOSK_MODEL_PATH=...
PORCUPINE_ACCESS_KEY=...
```

## Getting Help

1. Check `mark_x.log` for errors
2. Verify `.env` configuration
3. Test individual components
4. Review examples in this guide

## Success Checklist

- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] OpenRouter API key added
- [ ] At least one bot (Telegram/Discord) configured
- [ ] Application starts without errors
- [ ] Bot responds to messages
- [ ] Skills are loaded
- [ ] Database is created

Once all items are checked, you're ready to use Mark-X Enhanced!

---

**Need help?** Check the logs, review the configuration, and test step by step.

**Ready to build?** Start creating custom skills and make Jarvis truly yours!
