#!/usr/bin/env python3
"""
Script to update existing tasks with default priorities.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.task import Task

def update_task_priorities():
    """Update existing tasks with default priorities based on their type."""
    app = create_app()

    with app.app_context():
        # Get all tasks that don't have a priority set (should be none after migration, but just in case)
        tasks = Task.query.filter(Task.priority.is_(None)).all()

        if not tasks:
            print("No tasks found without priority. All tasks should have priority set.")
            return

        print(f"Found {len(tasks)} tasks without priority. Updating...")

        # Priority mapping based on task type
        priority_map = {
            'generate_document': 'normal',
            'sync_repository': 'low',
            'analyze_code': 'normal'
        }

        updated_count = 0
        for task in tasks:
            priority = priority_map.get(task.type, 'normal')
            task.priority = priority
            updated_count += 1
            print(f"Updated task {task.id} ({task.type}) with priority: {priority}")

        db.session.commit()
        print(f"Successfully updated {updated_count} tasks with default priorities.")

if __name__ == '__main__':
    update_task_priorities()
