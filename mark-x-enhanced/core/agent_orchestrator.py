"""Agent orchestrator for Mark-X Enhanced."""

import asyncio
import logging
from typing import Dict, Any, Optional
import json
import requests

from core.config import settings
from core.skills_loader import skills_loader
from core.scheduler import scheduler
from memory.persistent_db import db
from integrations.telegram_bot import TelegramBot
from integrations.discord_bot import DiscordBot

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Central orchestrator for all agents and components."""
    
    def __init__(self):
        self.telegram_bot = None
        self.discord_bot = None
        self.running = False
    
    async def initialize(self):
        """Initialize all components."""
        logger.info("Initializing Agent Orchestrator...")
        
        # Load skills
        skills_loader.reload_skills()
        logger.info(f"Loaded {len(skills_loader.get_all_skills())} skills")
        
        # Start scheduler
        scheduler.start()
        
        # Initialize messaging bots
        if settings.telegram_bot_token:
            self.telegram_bot = TelegramBot(message_callback=self.process_message)
        
        if settings.discord_bot_token:
            self.discord_bot = DiscordBot(message_callback=self.process_message)
        
        logger.info("Agent Orchestrator initialized")
    
    async def start(self):
        """Start all services."""
        if self.running:
            logger.warning("Agent Orchestrator already running")
            return
        
        self.running = True
        logger.info("Starting Agent Orchestrator...")
        
        tasks = []
        
        # Start Telegram bot
        if self.telegram_bot:
            tasks.append(asyncio.create_task(self.telegram_bot.start()))
        
        # Start Discord bot
        if self.discord_bot:
            tasks.append(asyncio.create_task(self.discord_bot.start()))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Agent Orchestrator started")
    
    async def stop(self):
        """Stop all services."""
        if not self.running:
            return
        
        logger.info("Stopping Agent Orchestrator...")
        
        # Stop scheduler
        scheduler.stop()
        
        # Stop bots
        if self.telegram_bot:
            await self.telegram_bot.stop()
        
        if self.discord_bot:
            await self.discord_bot.stop()
        
        self.running = False
        logger.info("Agent Orchestrator stopped")
    
    async def process_message(
        self,
        text: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Process a message from any platform.
        
        Args:
            text: User message text
            user_id: User ID
            context: Platform-specific context
            
        Returns:
            Response text
        """
        platform = context.get("platform", "unknown")
        logger.info(f"Processing message from {platform}: {text}")
        
        try:
            # Get LLM response with skill detection
            llm_response = await self._get_llm_response(text, user_id, context)
            
            intent = llm_response.get("intent", "chat")
            skill_name = llm_response.get("skill_name")
            parameters = llm_response.get("parameters", {})
            response_text = llm_response.get("text", "I'm not sure how to help with that, sir.")
            
            # Log conversation
            db.add_conversation(
                user_input=text,
                ai_response=response_text,
                intent=intent,
                skill_name=skill_name,
                parameters=parameters,
                platform=platform,
                user_id=user_id
            )
            
            # Execute skill if needed
            if skill_name and skill_name != "chat":
                skill = skills_loader.get_skill(skill_name)
                if skill:
                    # Execute skill asynchronously
                    asyncio.create_task(self._execute_skill(skill, parameters, context))
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "Sorry sir, I encountered an error processing your request."
    
    async def _get_llm_response(
        self,
        user_text: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get LLM response with skill detection.
        
        Returns:
            Dictionary with intent, skill_name, parameters, text
        """
        # Get user memory
        user_memory = db.get_user_memory_dict()
        
        # Get recent conversations
        recent_convs = db.get_recent_conversations(limit=5, platform=context.get("platform"))
        recent_history = "\n".join([
            f"User: {c.user_input}\nAI: {c.ai_response}"
            for c in recent_convs
        ])
        
        # Get available skills
        skills_info = skills_loader.get_skills_for_llm()
        
        # Build prompt
        system_prompt = self._build_system_prompt(skills_info)
        user_prompt = self._build_user_prompt(user_text, user_memory, recent_history)
        
        # Call LLM API (OpenRouter)
        try:
            response = await self._call_llm_api(system_prompt, user_prompt)
            return self._parse_llm_response(response)
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return {
                "intent": "chat",
                "skill_name": "chat",
                "parameters": {},
                "text": f"I'm having trouble connecting to my intelligence core, sir. Error: {str(e)}"
            }
    
    def _build_system_prompt(self, skills_info: list) -> str:
        """Build system prompt with skills information."""
        skills_desc = "\n".join([
            f"- {s['name']}: {s['description']}"
            for s in skills_info
        ])
        
        return f"""You are Jarvis, an advanced AI assistant. You are helpful, professional, and address the user as "sir".

Available skills:
{skills_desc}

When the user requests something, determine:
1. The intent/skill to use
2. Required parameters
3. A natural response

Respond in JSON format:
{{
    "intent": "skill_name or chat",
    "skill_name": "skill_name or null",
    "parameters": {{}},
    "text": "your response to the user",
    "memory_update": {{}} (optional, to store new information about the user)
}}"""
    
    def _build_user_prompt(
        self,
        user_text: str,
        memory: Dict,
        history: str
    ) -> str:
        """Build user prompt with context."""
        memory_str = json.dumps(memory, indent=2) if memory else "None"
        history_str = history if history else "No previous conversation"
        
        return f"""User memory: {memory_str}

Recent conversation:
{history_str}

User message: "{user_text}"

Determine the appropriate skill and parameters, and provide a response."""
    
    async def _call_llm_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call LLM API (OpenRouter)."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 500
        }
        
        # Use asyncio to run requests in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(url, headers=headers, json=payload, timeout=30)
        )
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM JSON response."""
        try:
            # Extract JSON from response
            if "```json" in response_text:
                start = response_text.index("```json") + 7
                end = response_text.index("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.index("```") + 3
                end = response_text.index("```", start)
                response_text = response_text[start:end].strip()
            
            # Find JSON object
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            json_str = response_text[start:end]
            
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {
                "intent": "chat",
                "skill_name": "chat",
                "parameters": {},
                "text": response_text
            }
    
    async def _execute_skill(
        self,
        skill,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """Execute a skill asynchronously."""
        try:
            import time
            start_time = time.time()
            
            result = await skill.execute(parameters, context)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log skill execution
            db.log_skill_execution(
                skill_name=skill.name,
                parameters=parameters,
                success=result.success,
                result_data=result.data,
                error_message=None if result.success else result.message,
                execution_time_ms=execution_time
            )
            
            logger.info(f"Skill {skill.name} executed: {result.success}")
            
        except Exception as e:
            logger.error(f"Error executing skill {skill.name}: {e}", exc_info=True)
            db.log_skill_execution(
                skill_name=skill.name,
                parameters=parameters,
                success=False,
                error_message=str(e),
                execution_time_ms=0
            )


# Global orchestrator instance
orchestrator = AgentOrchestrator()
