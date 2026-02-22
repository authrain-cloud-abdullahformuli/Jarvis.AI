"""Task scheduler for Mark-X Enhanced."""

import logging
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from core.config import settings
from memory.persistent_db import db

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled tasks and reminders."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running = False
    
    def start(self):
        """Start the scheduler."""
        if not self.running and settings.scheduler_enabled:
            self.scheduler.start()
            self.running = True
            self._load_persisted_tasks()
            logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            logger.info("Task scheduler stopped")
    
    def _load_persisted_tasks(self):
        """Load scheduled tasks from database."""
        tasks = db.get_active_tasks()
        for task in tasks:
            try:
                # TODO: This would need to be connected to skill execution
                # For now, just log that we found a task
                logger.info(f"Found persisted task: {task.task_name}")
            except Exception as e:
                logger.error(f"Failed to load task {task.task_name}: {e}")
    
    def add_once(
        self,
        func: Callable,
        run_at: datetime,
        task_id: Optional[str] = None,
        args: tuple = (),
        kwargs: Optional[Dict] = None
    ) -> str:
        """Schedule a one-time task.
        
        Args:
            func: Function to execute
            run_at: When to run the task
            task_id: Optional custom task ID
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            Task ID
        """
        trigger = DateTrigger(run_date=run_at)
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            args=args,
            kwargs=kwargs or {},
            id=task_id
        )
        logger.info(f"Scheduled one-time task {job.id} for {run_at}")
        return job.id
    
    def add_daily(
        self,
        func: Callable,
        hour: int = 0,
        minute: int = 0,
        task_id: Optional[str] = None,
        args: tuple = (),
        kwargs: Optional[Dict] = None
    ) -> str:
        """Schedule a daily task.
        
        Args:
            func: Function to execute
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            task_id: Optional custom task ID
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            Task ID
        """
        trigger = CronTrigger(hour=hour, minute=minute)
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            args=args,
            kwargs=kwargs or {},
            id=task_id
        )
        logger.info(f"Scheduled daily task {job.id} for {hour:02d}:{minute:02d}")
        return job.id
    
    def add_interval(
        self,
        func: Callable,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        task_id: Optional[str] = None,
        args: tuple = (),
        kwargs: Optional[Dict] = None
    ) -> str:
        """Schedule a recurring task with interval.
        
        Args:
            func: Function to execute
            seconds: Interval in seconds
            minutes: Interval in minutes
            hours: Interval in hours
            task_id: Optional custom task ID
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            Task ID
        """
        trigger = IntervalTrigger(seconds=seconds, minutes=minutes, hours=hours)
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            args=args,
            kwargs=kwargs or {},
            id=task_id
        )
        logger.info(f"Scheduled interval task {job.id} every {hours}h {minutes}m {seconds}s")
        return job.id
    
    def add_cron(
        self,
        func: Callable,
        cron_expression: str,
        task_id: Optional[str] = None,
        args: tuple = (),
        kwargs: Optional[Dict] = None
    ) -> str:
        """Schedule a task with cron expression.
        
        Args:
            func: Function to execute
            cron_expression: Cron expression (e.g., "0 9 * * mon-fri")
            task_id: Optional custom task ID
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            Task ID
        """
        trigger = CronTrigger.from_crontab(cron_expression)
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            args=args,
            kwargs=kwargs or {},
            id=task_id
        )
        logger.info(f"Scheduled cron task {job.id} with expression: {cron_expression}")
        return job.id
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task.
        
        Args:
            task_id: Task ID to remove
            
        Returns:
            True if removed, False if not found
        """
        try:
            self.scheduler.remove_job(task_id)
            logger.info(f"Removed task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove task {task_id}: {e}")
            return False
    
    def get_all_tasks(self) -> list:
        """Get all scheduled tasks."""
        return self.scheduler.get_jobs()
    
    def pause_task(self, task_id: str):
        """Pause a task."""
        self.scheduler.pause_job(task_id)
        logger.info(f"Paused task {task_id}")
    
    def resume_task(self, task_id: str):
        """Resume a paused task."""
        self.scheduler.resume_job(task_id)
        logger.info(f"Resumed task {task_id}")
    
    def schedule_reminder(
        self,
        message: str,
        remind_at: datetime,
        callback: Callable,
        reminder_id: Optional[str] = None
    ) -> str:
        """Schedule a reminder.
        
        Args:
            message: Reminder message
            remind_at: When to send reminder
            callback: Function to call with reminder message
            reminder_id: Optional custom reminder ID
            
        Returns:
            Reminder ID
        """
        return self.add_once(
            func=callback,
            run_at=remind_at,
            task_id=reminder_id,
            kwargs={"message": message}
        )


# Global scheduler instance
scheduler = TaskScheduler()
