#!/usr/bin/env python3
"""
Test script for repository API endpoint to verify error handling.
"""

import requests
import json
import time

def test_repository_statistics_api():
    """Test the repository statistics API endpoint."""

    # Base URL for the API
    base_url = "http://localhost:5000"

    # Test data
    test_user = {
        "username": "testuser",
        "password": "testpass123"
    }

    try:
        # First, try to login to get a session
        print("Testing repository statistics API...")

        # Test the statistics endpoint directly (this might fail without authentication)
        response = requests.get(f"{base_url}/api/repositories/statistics")
        print(f"Statistics endpoint response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Statistics data: {json.dumps(data, indent=2)}")
        else:
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_repository_statistics_api()
