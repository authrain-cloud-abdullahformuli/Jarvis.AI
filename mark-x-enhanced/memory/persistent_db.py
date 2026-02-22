"""Persistent database management for Mark-X Enhanced."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

from core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class Conversation(Base):
    """Conversation history table."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text)
    intent = Column(String(100))
    skill_name = Column(String(100))
    parameters = Column(JSON)
    platform = Column(String(50), default="voice")  # voice, telegram, discord, etc.
    user_id = Column(String(100))
    success = Column(Boolean, default=True)


class UserMemory(Base):
    """Long-term user memory table."""
    __tablename__ = "user_memory"
    
    id = Column(Integer, primary_key=True)
    category = Column(String(100), nullable=False)  # identity, preferences, relationships, etc.
    key = Column(String(200), nullable=False)
    value = Column(JSON, nullable=False)
    confidence = Column(Integer, default=100)  # 0-100 confidence score
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScheduledTask(Base):
    """Scheduled tasks table."""
    __tablename__ = "scheduled_tasks"
    
    id = Column(Integer, primary_key=True)
    task_name = Column(String(200), nullable=False)
    skill_name = Column(String(100), nullable=False)
    parameters = Column(JSON)
    schedule_type = Column(String(50))  # once, daily, weekly, cron
    schedule_value = Column(String(200))  # cron expression or datetime
    next_run = Column(DateTime)
    last_run = Column(DateTime)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SkillExecution(Base):
    """Skill execution history."""
    __tablename__ = "skill_executions"
    
    id = Column(Integer, primary_key=True)
    skill_name = Column(String(100), nullable=False)
    parameters = Column(JSON)
    success = Column(Boolean, default=True)
    result_data = Column(JSON)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class PersistentDB:
    """Persistent database manager."""
    
    def __init__(self):
        self.engine = create_engine(settings.get_database_url(), echo=settings.debug)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    # Conversation methods
    def add_conversation(
        self,
        user_input: str,
        ai_response: str,
        intent: Optional[str] = None,
        skill_name: Optional[str] = None,
        parameters: Optional[Dict] = None,
        platform: str = "voice",
        user_id: Optional[str] = None,
        success: bool = True
    ) -> Conversation:
        """Add a conversation entry."""
        session = self.get_session()
        try:
            conversation = Conversation(
                user_input=user_input,
                ai_response=ai_response,
                intent=intent,
                skill_name=skill_name,
                parameters=parameters,
                platform=platform,
                user_id=user_id,
                success=success
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation
        finally:
            session.close()
    
    def get_recent_conversations(self, limit: int = 10, platform: Optional[str] = None) -> List[Conversation]:
        """Get recent conversations."""
        session = self.get_session()
        try:
            query = session.query(Conversation).order_by(Conversation.timestamp.desc())
            if platform:
                query = query.filter(Conversation.platform == platform)
            return query.limit(limit).all()
        finally:
            session.close()
    
    # User Memory methods
    def set_user_memory(self, category: str, key: str, value: Any, confidence: int = 100):
        """Set or update user memory."""
        session = self.get_session()
        try:
            memory = session.query(UserMemory).filter_by(category=category, key=key).first()
            if memory:
                memory.value = value
                memory.confidence = confidence
                memory.last_updated = datetime.utcnow()
            else:
                memory = UserMemory(
                    category=category,
                    key=key,
                    value=value,
                    confidence=confidence
                )
                session.add(memory)
            session.commit()
        finally:
            session.close()
    
    def get_user_memory(self, category: Optional[str] = None, key: Optional[str] = None) -> List[UserMemory]:
        """Get user memory."""
        session = self.get_session()
        try:
            query = session.query(UserMemory)
            if category:
                query = query.filter(UserMemory.category == category)
            if key:
                query = query.filter(UserMemory.key == key)
            return query.all()
        finally:
            session.close()
    
    def get_user_memory_dict(self) -> Dict[str, Dict[str, Any]]:
        """Get all user memory as nested dictionary."""
        memories = self.get_user_memory()
        result = {}
        for memory in memories:
            if memory.category not in result:
                result[memory.category] = {}
            result[memory.category][memory.key] = {
                "value": memory.value,
                "confidence": memory.confidence,
                "last_updated": memory.last_updated
            }
        return result
    
    # Scheduled Task methods
    def add_scheduled_task(
        self,
        task_name: str,
        skill_name: str,
        schedule_type: str,
        schedule_value: str,
        parameters: Optional[Dict] = None,
        next_run: Optional[datetime] = None
    ) -> ScheduledTask:
        """Add a scheduled task."""
        session = self.get_session()
        try:
            task = ScheduledTask(
                task_name=task_name,
                skill_name=skill_name,
                parameters=parameters,
                schedule_type=schedule_type,
                schedule_value=schedule_value,
                next_run=next_run
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task
        finally:
            session.close()
    
    def get_active_tasks(self) -> List[ScheduledTask]:
        """Get all active scheduled tasks."""
        session = self.get_session()
        try:
            return session.query(ScheduledTask).filter(ScheduledTask.enabled == True).all()
        finally:
            session.close()
    
    # Skill Execution methods
    def log_skill_execution(
        self,
        skill_name: str,
        parameters: Dict,
        success: bool,
        result_data: Optional[Dict] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ):
        """Log a skill execution."""
        session = self.get_session()
        try:
            execution = SkillExecution(
                skill_name=skill_name,
                parameters=parameters,
                success=success,
                result_data=result_data,
                error_message=error_message,
                execution_time_ms=execution_time_ms
            )
            session.add(execution)
            session.commit()
        finally:
            session.close()


# Global database instance
db = PersistentDB()
