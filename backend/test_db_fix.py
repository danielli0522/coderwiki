#!/usr/bin/env python3
"""
Test script to verify database schema fixes
"""
import sys
import time
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app import create_app, db
from app.models.repository import Repository
from app.models.document import Document
from app.models.user import User

def test_database_schema():
    """Test that the database schema is working correctly."""
    app = create_app()

    with app.app_context():
        try:
            # Test 1: Check if we can query repositories without errors
            print("Testing repositories query...")
            repos = Repository.query.limit(5).all()
            print(f"✅ Successfully queried {len(repos)} repositories")

            # Test 2: Check if we can query documents without errors
            print("Testing documents query...")
            docs = Document.query.limit(5).all()
            print(f"✅ Successfully queried {len(docs)} documents")

            # Test 3: Check if we can query users without errors
            print("Testing users query...")
            users = User.query.limit(5).all()
            print(f"✅ Successfully queried {len(users)} users")

            # Test 4: Test repository creation with new schema
            print("Testing repository creation...")
            timestamp = int(time.time())
            test_repo = Repository(
                user_id=1,
                name=f"test-repo-{timestamp}",
                url=f"https://github.com/test/test-repo-{timestamp}",
                description="Test repository"
            )
            db.session.add(test_repo)
            db.session.commit()
            print("✅ Successfully created test repository")

            # Test 5: Test document creation with new schema
            print("Testing document creation...")
            test_doc = Document(
                repository_id=test_repo.id,
                user_id=1,
                title="Test Document",
                content="Test content",
                version="1.0",
                generated_at=datetime.utcnow()
            )
            db.session.add(test_doc)
            db.session.commit()
            print("✅ Successfully created test document")

            # Clean up test data
            db.session.delete(test_doc)
            db.session.delete(test_repo)
            db.session.commit()
            print("✅ Successfully cleaned up test data")

            print("\n🎉 All database schema tests passed!")
            return True

        except Exception as e:
            print(f"❌ Database schema test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_database_schema()
    sys.exit(0 if success else 1)
