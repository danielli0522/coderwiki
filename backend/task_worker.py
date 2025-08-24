#!/usr/bin/env python3
"""
Task Worker Process - Standalone task worker for processing background tasks.
"""

import os
import sys
import time
import signal
import argparse
from datetime import datetime, timezone

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.services.task_worker import TaskWorker
from app.services.task_scheduler import TaskScheduler
from app.models.user import User
from app.models.repository import Repository


class TaskWorkerProcess:
    """Task worker process for running background tasks."""

    def __init__(self, config_name='development', max_concurrent_tasks=3, task_timeout=1800):
        """Initialize task worker process.

        Args:
            config_name: Configuration name
            max_concurrent_tasks: Maximum concurrent tasks
            task_timeout: Task timeout in seconds
        """
        # Import config class based on config_name
        if config_name == 'development':
            from config import DevelopmentConfig
            config_class = DevelopmentConfig
        elif config_name == 'production':
            from config import ProductionConfig
            config_class = ProductionConfig
        elif config_name == 'testing':
            from config import TestingConfig
            config_class = TestingConfig
        else:
            from config import DevelopmentConfig
            config_class = DevelopmentConfig

        self.app = create_app(config_class)
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_timeout = task_timeout
        self.worker = None
        self.scheduler = None
        self.is_running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Initialize database
        with self.app.app_context():
            db.create_all()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Start the task worker process."""
        if self.is_running:
            return

        print("Starting Task Worker Process...")
        print(f"Max concurrent tasks: {self.max_concurrent_tasks}")
        print(f"Task timeout: {self.task_timeout} seconds")

        # Initialize worker and scheduler
        self.worker = TaskWorker(
            app=self.app,
            max_concurrent_tasks=self.max_concurrent_tasks,
            task_timeout=self.task_timeout
        )

        self.scheduler = TaskScheduler(self.worker)

        # Start worker
        self.worker.start()

        # Start scheduler
        self.scheduler.start()

        self.is_running = True

        print("Task Worker Process started successfully")

        # Create default schedules if needed
        self._create_default_schedules()

    def stop(self):
        """Stop the task worker process."""
        if not self.is_running:
            return

        print("Stopping Task Worker Process...")

        if self.scheduler:
            self.scheduler.stop()

        if self.worker:
            self.worker.stop()

        self.is_running = False
        print("Task Worker Process stopped")

    def _create_default_schedules(self):
        """Create default scheduled tasks."""
        try:
            # Create daily sync schedule for all repositories
            schedule_id = self.scheduler.create_daily_sync_schedule(
                name="Daily Repository Sync",
                hour=2,  # 2 AM
                minute=0
            )
            print(f"Created daily sync schedule: {schedule_id}")

            # Create daily analysis schedule
            schedule_id = self.scheduler.create_daily_analysis_schedule(
                name="Daily Code Analysis",
                hour=3,  # 3 AM
                minute=0
            )
            print(f"Created daily analysis schedule: {schedule_id}")

        except Exception as e:
            print(f"Error creating default schedules: {e}")

    def run(self):
        """Run the task worker process."""
        self.start()

        try:
            while self.is_running:
                # Print status every 30 seconds
                time.sleep(30)

                if self.worker and self.scheduler:
                    worker_status = self.worker.get_status()
                    scheduler_status = self.scheduler.get_status()

                    print(f"\n[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] Status Update:")
                    print(f"Worker: {'Running' if worker_status['is_running'] else 'Stopped'}")
                    print(f"Scheduler: {'Running' if scheduler_status['is_running'] else 'Stopped'}")
                    print(f"Queue: {worker_status['queue_status']['running_tasks']} running, {worker_status['queue_status']['queued_tasks']} queued")
                    print(f"Completed: {worker_status['queue_status']['stats']['completed_tasks']}")
                    print(f"Failed: {worker_status['queue_status']['stats']['failed_tasks']}")

        except KeyboardInterrupt:
            print("\nReceived interrupt signal")
        finally:
            self.stop()

    def get_status(self):
        """Get current status of the worker process."""
        if not self.worker or not self.scheduler:
            return {'error': 'Worker not started'}

        worker_status = self.worker.get_status()
        scheduler_status = self.scheduler.get_status()

        return {
            'is_running': self.is_running,
            'worker': worker_status,
            'scheduler': scheduler_status,
            'started_at': datetime.now(timezone.utc).isoformat()
        }


def main():
    """Main entry point for the task worker process."""
    parser = argparse.ArgumentParser(description='Task Worker Process')
    parser.add_argument('--config', default='development', help='Configuration name')
    parser.add_argument('--max-concurrent', type=int, default=3, help='Maximum concurrent tasks')
    parser.add_argument('--timeout', type=int, default=1800, help='Task timeout in seconds')
    parser.add_argument('--status', action='store_true', help='Show status and exit')

    args = parser.parse_args()

    # Create worker process
    worker_process = TaskWorkerProcess(
        config_name=args.config,
        max_concurrent_tasks=args.max_concurrent,
        task_timeout=args.timeout
    )

    if args.status:
        # Show status and exit
        status = worker_process.get_status()
        print("Task Worker Status:")
        print(f"Running: {status.get('is_running', False)}")
        if 'worker' in status:
            worker = status['worker']
            print(f"Max concurrent tasks: {worker.get('max_concurrent_tasks', 0)}")
            print(f"Task timeout: {worker.get('task_timeout', 0)} seconds")
            if 'queue_status' in worker:
                queue = worker['queue_status']
                print(f"Running tasks: {queue.get('running_tasks', 0)}")
                print(f"Queued tasks: {queue.get('queued_tasks', 0)}")
                print(f"Completed tasks: {queue['stats'].get('completed_tasks', 0)}")
                print(f"Failed tasks: {queue['stats'].get('failed_tasks', 0)}")
        return

    # Run the worker process
    worker_process.run()


if __name__ == '__main__':
    main()
