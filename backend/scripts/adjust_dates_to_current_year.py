#!/usr/bin/env python3
"""
Script to adjust existing task dates to the current year (2024).
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.task import Task
from datetime import datetime, timezone, timedelta

def adjust_dates_to_current_year():
    """Adjust existing task dates to the current year (2024)."""
    app = create_app()

    with app.app_context():
        # Get all tasks
        tasks = Task.query.all()

        if not tasks:
            print("No tasks found.")
            return

        print(f"Found {len(tasks)} tasks. Adjusting dates to current year...")

        # Calculate the year difference (2025 -> 2024)
        year_adjustment = -1

        adjusted_count = 0
        for task in tasks:
            needs_adjustment = False

            # Adjust created_at
            if task.created_at and task.created_at.year == 2025:
                task.created_at = task.created_at.replace(year=2024)
                needs_adjustment = True

            # Adjust updated_at
            if task.updated_at and task.updated_at.year == 2025:
                task.updated_at = task.updated_at.replace(year=2024)
                needs_adjustment = True

            # Adjust started_at
            if task.started_at and task.started_at.year == 2025:
                task.started_at = task.started_at.replace(year=2024)
                needs_adjustment = True

            # Adjust completed_at
            if task.completed_at and task.completed_at.year == 2025:
                task.completed_at = task.completed_at.replace(year=2024)
                needs_adjustment = True

            if needs_adjustment:
                adjusted_count += 1
                print(f"Adjusted dates for task {task.id}: {task.created_at}")

        if adjusted_count > 0:
            db.session.commit()
            print(f"Successfully adjusted dates for {adjusted_count} tasks.")
        else:
            print("No tasks needed date adjustment.")

if __name__ == '__main__':
    adjust_dates_to_current_year()
