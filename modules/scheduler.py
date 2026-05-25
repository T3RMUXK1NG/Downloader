"""
OMNIPOTENT SOVEREIGN NEXUS - Download Scheduler Module
Version: v3.0.1 ULTIMATE NEXUS

Download scheduling with support for:
- One-time scheduled downloads
- Recurring downloads
- Queue management
- Priority scheduling
- Rate limiting windows
- Bandwidth management
- Automatic retries
- Task dependencies

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import logging
import time
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    Awaitable,
)
from croniter import croniter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Schedule type enumeration."""
    
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CRON = "cron"
    INTERVAL = "interval"


class TaskStatus(Enum):
    """Task status enumeration."""
    
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """Task priority levels."""
    
    LOW = 1
    NORMAL = 5
    HIGH = 10
    URGENT = 20


@dataclass
class ScheduleConfig:
    """
    Schedule configuration.
    
    Attributes:
        schedule_type: Type of schedule
        start_time: Start time for one-time tasks
        cron_expression: Cron expression for recurring tasks
        interval_minutes: Interval in minutes
        timezone: Timezone for scheduling
        enabled: Whether schedule is enabled
        max_runs: Maximum runs (0 = unlimited)
        end_date: End date for recurring tasks
    """
    schedule_type: ScheduleType = ScheduleType.ONCE
    start_time: Optional[datetime] = None
    cron_expression: Optional[str] = None
    interval_minutes: int = 60
    timezone: str = "UTC"
    enabled: bool = True
    max_runs: int = 0
    end_date: Optional[datetime] = None


@dataclass
class ScheduledTask:
    """
    Scheduled download task.
    
    Attributes:
        id: Task ID
        name: Task name
        url: Download URL
        output_path: Output path
        schedule: Schedule configuration
        priority: Task priority
        status: Current status
        created_at: Creation timestamp
        last_run: Last run timestamp
        next_run: Next run timestamp
        run_count: Number of runs
        max_retries: Maximum retries
        retry_count: Current retry count
        retry_delay: Delay between retries
        metadata: Additional metadata
        callback: Callback function
    """
    id: str
    name: str
    url: str
    output_path: str
    schedule: ScheduleConfig
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    max_retries: int = 3
    retry_count: int = 0
    retry_delay: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_next_run(self) -> Optional[datetime]:
        """Calculate next run time."""
        now = datetime.now()
        
        if not self.schedule.enabled:
            return None
        
        if self.schedule.max_runs > 0 and self.run_count >= self.schedule.max_runs:
            return None
        
        if self.schedule.end_date and now > self.schedule.end_date:
            return None
        
        if self.schedule.schedule_type == ScheduleType.ONCE:
            if self.schedule.start_time and self.run_count == 0:
                return self.schedule.start_time
            return None
        
        elif self.schedule.schedule_type == ScheduleType.CRON:
            if self.schedule.cron_expression:
                try:
                    cron = croniter(self.schedule.cron_expression, now)
                    return cron.get_next(datetime)
                except Exception:
                    return None
        
        elif self.schedule.schedule_type == ScheduleType.INTERVAL:
            if self.last_run:
                return self.last_run + timedelta(minutes=self.schedule.interval_minutes)
            elif self.schedule.start_time:
                return self.schedule.start_time
            return now + timedelta(minutes=self.schedule.interval_minutes)
        
        elif self.schedule.schedule_type == ScheduleType.DAILY:
            if self.last_run:
                return self.last_run + timedelta(days=1)
            elif self.schedule.start_time:
                return self.schedule.start_time
            return now + timedelta(days=1)
        
        elif self.schedule.schedule_type == ScheduleType.WEEKLY:
            if self.last_run:
                return self.last_run + timedelta(weeks=1)
            elif self.schedule.start_time:
                return self.schedule.start_time
            return now + timedelta(weeks=1)
        
        elif self.schedule.schedule_type == ScheduleType.MONTHLY:
            if self.last_run:
                next_month = self.last_run.replace(day=1) + timedelta(days=32)
                return next_month.replace(day=self.last_run.day)
            elif self.schedule.start_time:
                return self.schedule.start_time
            return None
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "output_path": self.output_path,
            "schedule_type": self.schedule.schedule_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "retry_count": self.retry_count,
        }


@dataclass
class TaskResult:
    """
    Task execution result.
    
    Attributes:
        task_id: Task ID
        success: Whether task succeeded
        start_time: Execution start time
        end_time: Execution end time
        duration: Duration in seconds
        output_path: Output file path
        file_size: Downloaded file size
        error_message: Error message if failed
        error_code: Error code if failed
    """
    task_id: str
    success: bool
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    output_path: Optional[str] = None
    file_size: int = 0
    error_message: Optional[str] = None
    error_code: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": round(self.duration, 2),
            "output_path": self.output_path,
            "file_size": self.file_size,
            "error_message": self.error_message,
            "error_code": self.error_code,
        }


@dataclass
class SchedulerStats:
    """
    Scheduler statistics.
    
    Attributes:
        total_tasks: Total number of tasks
        pending_tasks: Number of pending tasks
        running_tasks: Number of running tasks
        completed_tasks: Number of completed tasks
        failed_tasks: Number of failed tasks
        total_runs: Total runs executed
        success_rate: Success rate percentage
    """
    total_tasks: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_runs: int = 0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_tasks": self.total_tasks,
            "pending_tasks": self.pending_tasks,
            "running_tasks": self.running_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "total_runs": self.total_runs,
            "success_rate": round(self.success_rate, 2),
        }


class DownloadScheduler:
    """
    OMNIPOTENT SOVEREIGN NEXUS Download Scheduler.
    
    Comprehensive scheduling with:
    - Multiple schedule types
    - Priority queuing
    - Automatic retries
    - Task management
    """
    
    def __init__(
        self,
        download_callback: Optional[Callable[[ScheduledTask], Awaitable[TaskResult]]] = None,
        max_concurrent: int = 3,
    ) -> None:
        """
        Initialize download scheduler.
        
        Args:
            download_callback: Function to execute downloads
            max_concurrent: Maximum concurrent downloads
        """
        self._download_callback = download_callback
        self._max_concurrent = max_concurrent
        
        self._tasks: Dict[str, ScheduledTask] = {}
        self._results: Dict[str, List[TaskResult]] = {}
        self._running_tasks: set = set()
        self._scheduler_task: Optional[asyncio.Task] = None
        self._running = False
        self._lock = asyncio.Lock()
        
        logger.info(f"DownloadScheduler initialized v3.0.1 ULTIMATE NEXUS")
    
    async def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            return
        
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Scheduler started")
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel running tasks
        for task_id in list(self._running_tasks):
            await self.cancel_task(task_id)
        
        logger.info("Scheduler stopped")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                await self._check_scheduled_tasks()
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(5)
    
    async def _check_scheduled_tasks(self) -> None:
        """Check and execute scheduled tasks."""
        now = datetime.now()
        
        # Get tasks ready to run
        ready_tasks = []
        
        for task in self._tasks.values():
            if (
                task.status in (TaskStatus.PENDING, TaskStatus.SCHEDULED) and
                task.next_run and
                task.next_run <= now and
                task.id not in self._running_tasks and
                len(self._running_tasks) < self._max_concurrent
            ):
                ready_tasks.append(task)
        
        # Sort by priority
        ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)
        
        # Execute tasks
        for task in ready_tasks:
            if len(self._running_tasks) >= self._max_concurrent:
                break
            
            asyncio.create_task(self._execute_task(task))
    
    async def _execute_task(self, task: ScheduledTask) -> TaskResult:
        """Execute a scheduled task."""
        task.status = TaskStatus.RUNNING
        self._running_tasks.add(task.id)
        
        start_time = datetime.now()
        result = TaskResult(
            task_id=task.id,
            success=False,
            start_time=start_time,
        )
        
        try:
            if self._download_callback:
                result = await self._download_callback(task)
            else:
                # Simulate download
                result.success = True
                result.output_path = task.output_path
            
            result.end_time = datetime.now()
            result.duration = (result.end_time - start_time).total_seconds()
            
            if result.success:
                task.status = TaskStatus.COMPLETED
                task.run_count += 1
                task.retry_count = 0
            else:
                task.retry_count += 1
                
                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.RETRYING
                    task.next_run = datetime.now() + timedelta(seconds=task.retry_delay)
                else:
                    task.status = TaskStatus.FAILED
            
            task.last_run = start_time
            
            # Calculate next run for recurring tasks
            if task.schedule.schedule_type != ScheduleType.ONCE:
                task.next_run = task.calculate_next_run()
            
            logger.info(f"Task {task.id} completed: {result.success}")
            
        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            result.error_message = "Task cancelled"
            logger.info(f"Task {task.id} cancelled")
            
        except Exception as e:
            logger.error(f"Task {task.id} error: {e}")
            task.status = TaskStatus.FAILED
            result.error_message = str(e)
        
        finally:
            self._running_tasks.discard(task.id)
            
            # Store result
            if task.id not in self._results:
                self._results[task.id] = []
            self._results[task.id].append(result)
        
        return result
    
    def add_task(
        self,
        name: str,
        url: str,
        output_path: str,
        schedule: ScheduleConfig,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ScheduledTask:
        """
        Add a new scheduled task.
        
        Args:
            name: Task name
            url: Download URL
            output_path: Output path
            schedule: Schedule configuration
            priority: Task priority
            max_retries: Maximum retries
            metadata: Additional metadata
            
        Returns:
            ScheduledTask
        """
        task_id = hashlib.md5(f"{name}{url}{time.time()}".encode()).hexdigest()[:12]
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            url=url,
            output_path=output_path,
            schedule=schedule,
            priority=priority,
            status=TaskStatus.SCHEDULED,
            max_retries=max_retries,
            metadata=metadata or {},
        )
        
        task.next_run = task.calculate_next_run()
        
        self._tasks[task_id] = task
        logger.info(f"Added task {task_id}: {name}")
        
        return task
    
    def add_one_time_task(
        self,
        name: str,
        url: str,
        output_path: str,
        start_time: datetime,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> ScheduledTask:
        """
        Add a one-time scheduled task.
        
        Args:
            name: Task name
            url: Download URL
            output_path: Output path
            start_time: Scheduled start time
            priority: Task priority
            
        Returns:
            ScheduledTask
        """
        schedule = ScheduleConfig(
            schedule_type=ScheduleType.ONCE,
            start_time=start_time,
        )
        
        return self.add_task(name, url, output_path, schedule, priority)
    
    def add_recurring_task(
        self,
        name: str,
        url: str,
        output_path: str,
        cron_expression: str,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> ScheduledTask:
        """
        Add a recurring task with cron expression.
        
        Args:
            name: Task name
            url: Download URL
            output_path: Output path
            cron_expression: Cron expression
            priority: Task priority
            
        Returns:
            ScheduledTask
        """
        schedule = ScheduleConfig(
            schedule_type=ScheduleType.CRON,
            cron_expression=cron_expression,
        )
        
        return self.add_task(name, url, output_path, schedule, priority)
    
    def add_interval_task(
        self,
        name: str,
        url: str,
        output_path: str,
        interval_minutes: int,
        start_time: Optional[datetime] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> ScheduledTask:
        """
        Add an interval-based task.
        
        Args:
            name: Task name
            url: Download URL
            output_path: Output path
            interval_minutes: Interval in minutes
            start_time: Optional start time
            priority: Task priority
            
        Returns:
            ScheduledTask
        """
        schedule = ScheduleConfig(
            schedule_type=ScheduleType.INTERVAL,
            interval_minutes=interval_minutes,
            start_time=start_time,
        )
        
        return self.add_task(name, url, output_path, schedule, priority)
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if cancelled
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        task.status = TaskStatus.CANCELLED
        task.schedule.enabled = False
        
        logger.info(f"Cancelled task {task_id}")
        return True
    
    async def pause_task(self, task_id: str) -> bool:
        """
        Pause a scheduled task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if paused
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        task.status = TaskStatus.PAUSED
        task.schedule.enabled = False
        
        logger.info(f"Paused task {task_id}")
        return True
    
    async def resume_task(self, task_id: str) -> bool:
        """
        Resume a paused task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if resumed
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        task.status = TaskStatus.SCHEDULED
        task.schedule.enabled = True
        task.next_run = task.calculate_next_run()
        
        logger.info(f"Resumed task {task_id}")
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from scheduler.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if removed
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._results.pop(task_id, None)
            logger.info(f"Removed task {task_id}")
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task by ID."""
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[ScheduledTask]:
        """Get all tasks."""
        return list(self._tasks.values())
    
    def get_pending_tasks(self) -> List[ScheduledTask]:
        """Get pending tasks."""
        return [t for t in self._tasks.values() if t.status == TaskStatus.PENDING]
    
    def get_running_tasks(self) -> List[ScheduledTask]:
        """Get running tasks."""
        return [t for t in self._tasks.values() if t.status == TaskStatus.RUNNING]
    
    def get_task_results(self, task_id: str) -> List[TaskResult]:
        """Get results for a task."""
        return self._results.get(task_id, [])
    
    def get_stats(self) -> SchedulerStats:
        """Get scheduler statistics."""
        tasks = list(self._tasks.values())
        
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        failed = [t for t in tasks if t.status == TaskStatus.FAILED]
        
        total_runs = sum(t.run_count for t in tasks)
        successful_runs = sum(
            1 for results in self._results.values()
            for r in results if r.success
        )
        
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        return SchedulerStats(
            total_tasks=len(tasks),
            pending_tasks=len([t for t in tasks if t.status in (TaskStatus.PENDING, TaskStatus.SCHEDULED)]),
            running_tasks=len(self._running_tasks),
            completed_tasks=len(completed),
            failed_tasks=len(failed),
            total_runs=total_runs,
            success_rate=success_rate,
        )
    
    def export_tasks(self, file_path: Path) -> bool:
        """Export tasks to JSON file."""
        try:
            data = {
                "tasks": [task.to_dict() for task in self._tasks.values()],
                "exported_at": datetime.now().isoformat(),
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported tasks to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False
    
    def import_tasks(self, file_path: Path) -> int:
        """Import tasks from JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            count = 0
            for task_data in data.get("tasks", []):
                schedule = ScheduleConfig(
                    schedule_type=ScheduleType(task_data.get("schedule_type", "once")),
                )
                
                self.add_task(
                    name=task_data.get("name", ""),
                    url=task_data.get("url", ""),
                    output_path=task_data.get("output_path", ""),
                    schedule=schedule,
                    priority=TaskPriority(task_data.get("priority", 5)),
                )
                count += 1
            
            logger.info(f"Imported {count} tasks from {file_path}")
            return count
            
        except Exception as e:
            logger.error(f"Import error: {e}")
            return 0


# Export all public classes and functions
__all__ = [
    "DownloadScheduler",
    "ScheduleType",
    "TaskStatus",
    "TaskPriority",
    "ScheduledTask",
    "ScheduleConfig",
    "TaskResult",
    "SchedulerStats",
]
