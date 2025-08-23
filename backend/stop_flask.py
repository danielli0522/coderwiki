#!/usr/bin/env python3
"""
Stop Flask Application Script
"""

import subprocess
import sys
import os

def stop_flask_app():
    """Stop the Flask application"""
    try:
        # Find and kill Python processes running run.py
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'python run.py' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    try:
                        os.kill(int(pid), 15)  # SIGTERM
                        print(f"✅ Stopped Flask application (PID: {pid})")
                    except ProcessLookupError:
                        print(f"⚠️  Process {pid} not found")
        
        # Also check for any remaining processes on port 5001
        try:
            result = subprocess.run(['lsof', '-ti', ':5001'], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        try:
                            os.kill(int(pid), 15)
                            print(f"✅ Stopped process on port 5001 (PID: {pid})")
                        except ProcessLookupError:
                            pass
        except FileNotFoundError:
            pass
        
        print("🎉 Flask application stopped successfully!")
        
    except Exception as e:
        print(f"❌ Error stopping Flask application: {e}")

if __name__ == '__main__':
    stop_flask_app()