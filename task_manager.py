import sqlite3
import os
import time
import json
import threading
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple

class TaskStatus(str, Enum):
    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

class TaskManager:
    def __init__(self, db_path="tasks.db"):
        self.db_path = db_path
        self.tasks_lock = threading.Lock()
        self.running_tasks = {}  # Store thread objects
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with the tasks table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                task_type TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL,
                started_at REAL,
                completed_at REAL,
                result TEXT,
                error TEXT
            )
            ''')
            conn.commit()
    
    def add_task(self, query: str, task_type: str) -> str:
        """Add a new task to the queue and return its ID."""
        task_id = str(uuid.uuid4())
        created_at = time.time()
        
        with self.tasks_lock, sqlite3.connect(self.db_path) as conn:
            # Check if we already have 5 tasks that are not completed or failed
            active_count = conn.execute('''
                SELECT COUNT(*) FROM tasks 
                WHERE status NOT IN (?, ?)
            ''', (TaskStatus.COMPLETED, TaskStatus.FAILED)).fetchone()[0]
            
            if active_count >= 5:
                raise ValueError("Maximum of 5 active tasks allowed. Please wait for some tasks to complete.")
            
            conn.execute('''
            INSERT INTO tasks (id, query, task_type, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (task_id, query, task_type, TaskStatus.QUEUED, created_at))
            conn.commit()
        
        return task_id
    
    def start_task(self, task_id: str, task_func, *args, **kwargs):
        """Start a task in a separate thread."""
        with self.tasks_lock, sqlite3.connect(self.db_path) as conn:
            # Check if task exists and is in QUEUED state
            task = conn.execute('SELECT status FROM tasks WHERE id = ?', (task_id,)).fetchone()
            if not task:
                raise ValueError(f"Task {task_id} not found")
            if task[0] != TaskStatus.QUEUED:
                raise ValueError(f"Task {task_id} is not in QUEUED state")
            
            # Update task status to RUNNING
            started_at = time.time()
            conn.execute('''
            UPDATE tasks SET status = ?, started_at = ?
            WHERE id = ?
            ''', (TaskStatus.RUNNING, started_at, task_id))
            conn.commit()
        
        # Start task in a separate thread
        thread = threading.Thread(
            target=self._run_task,
            args=(task_id, task_func) + args,
            kwargs=kwargs,
            daemon=True
        )
        self.running_tasks[task_id] = thread
        thread.start()
    
    def _run_task(self, task_id: str, task_func, *args, **kwargs):
        """Run the task and update its status when done."""
        try:
            result = task_func(*args, **kwargs)
            with self.tasks_lock, sqlite3.connect(self.db_path) as conn:
                completed_at = time.time()
                conn.execute('''
                UPDATE tasks SET status = ?, completed_at = ?, result = ?
                WHERE id = ?
                ''', (TaskStatus.COMPLETED, completed_at, result, task_id))
                conn.commit()
        except Exception as e:
            with self.tasks_lock, sqlite3.connect(self.db_path) as conn:
                completed_at = time.time()
                conn.execute('''
                UPDATE tasks SET status = ?, completed_at = ?, error = ?
                WHERE id = ?
                ''', (TaskStatus.FAILED, completed_at, str(e), task_id))
                conn.commit()
        finally:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task if it's still in QUEUED or RUNNING state."""
        with self.tasks_lock, sqlite3.connect(self.db_path) as conn:
            task = conn.execute('SELECT status FROM tasks WHERE id = ?', (task_id,)).fetchone()
            if not task:
                return False
            
            if task[0] in [TaskStatus.QUEUED, TaskStatus.RUNNING]:
                conn.execute('''
                UPDATE tasks SET status = ?, completed_at = ?
                WHERE id = ?
                ''', (TaskStatus.CANCELLED, time.time(), task_id))
                conn.commit()
                
                # If the task is running, we can't really stop the thread,
                # but we can mark it as cancelled in the database
                return True
            
            return False
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by its ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
            if not task:
                return None
            
            return dict(task)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks, ordered by creation time (newest first)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            tasks = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC').fetchall()
            return [dict(task) for task in tasks]
    
    def get_task_elapsed_time(self, task_id: str) -> Tuple[float, bool]:
        """
        Get the elapsed time for a task in seconds and whether it's still running.
        
        Returns:
            Tuple[float, bool]: (elapsed_time, is_running)
        """
        with sqlite3.connect(self.db_path) as conn:
            task = conn.execute('''
            SELECT status, created_at, started_at, completed_at
            FROM tasks WHERE id = ?
            ''', (task_id,)).fetchone()
            
            if not task:
                return 0, False
            
            status, created_at, started_at, completed_at = task
            
            if status == TaskStatus.QUEUED:
                return time.time() - created_at, True
            elif status == TaskStatus.RUNNING:
                start_time = started_at if started_at else created_at
                return time.time() - start_time, True
            else:  # COMPLETED, FAILED, or CANCELLED
                if completed_at and started_at:
                    return completed_at - started_at, False
                elif completed_at:
                    return completed_at - created_at, False
                else:
                    return 0, False
    
    def format_elapsed_time(self, seconds: float) -> str:
        """Format elapsed time in a human-readable format."""
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_task_brief(self, task_id: str) -> str:
        """Get a brief description of the task (first 10 words of query)."""
        with sqlite3.connect(self.db_path) as conn:
            task = conn.execute('SELECT query FROM tasks WHERE id = ?', (task_id,)).fetchone()
            if not task or not task[0]:
                return "Unknown task"
            
            words = task[0].split()
            if len(words) <= 10:
                return task[0]
            else:
                return " ".join(words[:10]) + "..."
    
    def cleanup_old_tasks(self, days_to_keep: int = 30):
        """Remove tasks older than the specified number of days."""
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        with self.tasks_lock, sqlite3.connect(self.db_path) as conn:
            conn.execute('''
            DELETE FROM tasks
            WHERE created_at < ? AND status IN (?, ?, ?)
            ''', (cutoff_time, TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED))
            conn.commit()

# Create a singleton instance
task_manager = TaskManager()
