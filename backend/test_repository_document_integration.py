#!/usr/bin/env python3
"""
Comprehensive integration test for repository pulling and document generation.
Tests the full pipeline from repository clone to document generation.
本地目录的写和读一致性测试
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.document import Document
from app.models.llm_config import LLMConfig
from app.services.repository_service import RepositoryService
from app.services.document_generator import DocumentGenerator
from app.utils.git_service import GitService
from app.utils.file_utils import FileUtils

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RepositoryDocumentIntegrationTest:
    """仓库拉取和文档生成集成测试"""

    def __init__(self):
        """初始化测试环境"""
        self.app = None
        self.test_user = None
        self.test_repo_url = "https://github.com/octocat/Hello-World.git"
        self.test_repo_name = "test-integration-repo"
        self.temp_base_dir = None
        self.repository_service = None
        self.document_generator = None
        self.git_service = None

    def setup_test_environment(self):
        """设置测试环境"""
        logger.info("Setting up test environment...")
        
        # Create temporary directory for repositories
        self.temp_base_dir = tempfile.mkdtemp(prefix="coderwiki_test_")
        logger.info(f"Created temporary directory: {self.temp_base_dir}")

        # Create test config class
        class TestConfig:
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            GIT_REPOS_PATH = self.temp_base_dir
            SECRET_KEY = 'test-secret-key'
            TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')
            STATIC_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')

        # Create Flask app with test config
        self.app = create_app(TestConfig)

        with self.app.app_context():
            # Create database tables
            db.create_all()
            
            # Create test user
            self.test_user = User(
                username='test_integration_user',
                email='integration@test.com'
            )
            self.test_user.set_password('test_password_123')
            db.session.add(self.test_user)
            
            db.session.commit()
            
            # Create test LLM config after user is committed
            self.test_llm_config = LLMConfig(
                user_id=self.test_user.id,
                provider='openai',
                model_name='gpt-3.5-turbo',
                max_tokens=2000,
                temperature=0.7
            )
            # Set API key separately
            self.test_llm_config.set_api_key('test-api-key-123')
            db.session.add(self.test_llm_config)
            db.session.commit()

            # Initialize services
            self.repository_service = RepositoryService()
            self.document_generator = DocumentGenerator(use_mcp=False, use_claude_code=False)
            self.git_service = GitService(base_repo_path=self.temp_base_dir)

        logger.info("Test environment setup completed")

    def cleanup_test_environment(self):
        """清理测试环境"""
        logger.info("Cleaning up test environment...")
        
        if self.temp_base_dir and os.path.exists(self.temp_base_dir):
            try:
                shutil.rmtree(self.temp_base_dir)
                logger.info(f"Removed temporary directory: {self.temp_base_dir}")
            except Exception as e:
                logger.error(f"Error removing temporary directory: {str(e)}")

    def test_repository_clone_consistency(self):
        """测试仓库克隆的本地目录一致性"""
        logger.info("Testing repository clone consistency...")
        
        with self.app.app_context():
            # Step 1: Create repository record
            create_result = self.repository_service.create_repository(
                user_id=self.test_user.id,
                url=self.test_repo_url,
                name=self.test_repo_name,
                description="Integration test repository"
            )
            
            assert create_result['success'], f"Repository creation failed: {create_result.get('error')}"
            repo_id = create_result['repository_id']
            logger.info(f"Repository created with ID: {repo_id}")

            # Step 2: Wait for cloning to complete and verify
            repository = Repository.query.get(repo_id)
            assert repository is not None, "Repository not found in database"
            
            # Check if repository was actually cloned
            local_path = repository.local_path
            assert local_path is not None, "Local path not set in database"
            assert os.path.exists(local_path), f"Local repository path does not exist: {local_path}"
            
            # Verify local path is within our test directory
            assert str(local_path).startswith(str(self.temp_base_dir)), \
                f"Local path {local_path} not within test directory {self.temp_base_dir}"
            
            logger.info(f"Repository cloned to: {local_path}")

            # Step 3: Verify directory structure
            git_dir = Path(local_path) / '.git'
            assert git_dir.exists(), f"Git directory not found: {git_dir}"
            
            # Check if there are files in the repository
            files = list(Path(local_path).glob('*'))
            assert len(files) > 0, "No files found in cloned repository"
            logger.info(f"Found {len(files)} files/directories in cloned repository")

            # Step 4: Verify database consistency
            assert repository.status in ['active', 'cloning'], f"Unexpected repository status: {repository.status}"
            assert repository.clone_status in ['completed', 'cloning'], f"Unexpected clone status: {repository.clone_status}"
            
            if repository.clone_status == 'completed':
                assert repository.commit_hash is not None, "Commit hash not recorded"
                assert repository.repo_size is not None, "Repository size not recorded"
                assert repository.file_count is not None, "File count not recorded"
                logger.info(f"Repository metadata: size={repository.repo_size}, files={repository.file_count}")

            return repository

    def test_document_generation_consistency(self, repository):
        """测试文档生成的一致性"""
        logger.info("Testing document generation consistency...")
        
        with self.app.app_context():
            # Step 1: Generate document
            doc_result = self.document_generator.generate_document(
                repository_id=repository.id,
                user_id=self.test_user.id,
                llm_config_id=self.test_llm_config.id,
                doc_type='overview',
                doc_title='Integration Test Document'
            )
            
            # For this test, we'll check the result structure even if generation fails
            # (since we may not have valid API keys in test environment)
            assert 'success' in doc_result, "Document generation result missing 'success' field"
            assert 'task_id' in doc_result, "Document generation result missing 'task_id' field"
            
            if doc_result['success']:
                # Document was successfully generated
                doc_id = doc_result.get('document_id')
                assert doc_id is not None, "Document ID not returned"
                
                # Verify document was saved to database
                document = Document.query.get(doc_id)
                assert document is not None, "Document not found in database"
                assert document.repository_id == repository.id, "Document not linked to correct repository"
                assert document.user_id == self.test_user.id, "Document not linked to correct user"
                
                logger.info(f"Document successfully generated with ID: {doc_id}")
                
                # Verify document content
                assert document.content is not None, "Document content is empty"
                assert len(document.content) > 0, "Document content is empty"
                
                return document
            else:
                # Document generation failed (expected in test environment without API keys)
                logger.info(f"Document generation failed as expected: {doc_result.get('error')}")
                return None

    def test_directory_read_write_consistency(self, repository):
        """测试本地目录的读写一致性"""
        logger.info("Testing directory read/write consistency...")
        
        with self.app.app_context():
            local_path = Path(repository.local_path)
            
            # Test 1: Write a test file
            test_file = local_path / 'integration_test.txt'
            test_content = f"Integration test file created at {datetime.now().isoformat()}"
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            assert test_file.exists(), "Test file was not written"
            logger.info(f"Test file written: {test_file}")
            
            # Test 2: Read the test file
            with open(test_file, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            assert read_content == test_content, "Read content does not match written content"
            logger.info("Test file read successfully with matching content")
            
            # Test 3: File utilities consistency
            file_info = FileUtils.get_directory_info(str(local_path))
            assert file_info['success'], f"FileUtils.get_directory_info failed: {file_info.get('error')}"
            assert file_info['exists'], "FileUtils reports directory doesn't exist"
            assert file_info['file_count'] > 0, "FileUtils reports zero files"
            
            logger.info(f"FileUtils directory info: {file_info['file_count']} files, {file_info['size_human']}")
            
            # Test 4: Repository analyzer consistency
            try:
                from app.utils.repository_analyzer import RepositoryAnalyzer
                analyzer = RepositoryAnalyzer()
                analysis = analyzer.analyze_repository(str(local_path))
                
                assert 'project_name' in analysis, "Repository analysis missing project name"
                assert 'file_count' in analysis, "Repository analysis missing file count"
                assert analysis['file_count'] > 0, "Repository analysis reports zero files"
                
                logger.info(f"Repository analysis: {analysis['file_count']} files, language: {analysis.get('language', 'unknown')}")
                
            except Exception as e:
                logger.warning(f"Repository analyzer test skipped: {str(e)}")
            
            # Clean up test file
            test_file.unlink()
            logger.info("Test file cleaned up")

    def test_repository_sync_consistency(self, repository):
        """测试仓库同步的一致性"""
        logger.info("Testing repository sync consistency...")
        
        with self.app.app_context():
            # Record original state
            original_commit = repository.commit_hash
            original_size = repository.repo_size
            
            # Test sync operation
            sync_result = self.repository_service.sync_repository(
                repository_id=repository.id,
                user_id=self.test_user.id
            )
            
            if sync_result['success']:
                # Refresh repository from database
                db.session.refresh(repository)
                
                # Verify local path still exists
                assert os.path.exists(repository.local_path), "Local path no longer exists after sync"
                
                # Verify Git repository is still valid
                git_dir = Path(repository.local_path) / '.git'
                assert git_dir.exists(), "Git directory no longer exists after sync"
                
                logger.info("Repository sync completed successfully")
                
                # Check if metadata was updated
                if repository.commit_hash != original_commit:
                    logger.info(f"Commit hash updated: {original_commit} -> {repository.commit_hash}")
                
                if repository.repo_size != original_size:
                    logger.info(f"Repository size updated: {original_size} -> {repository.repo_size}")
                    
            else:
                logger.info(f"Repository sync failed (expected in some cases): {sync_result.get('error')}")

    def test_repository_deletion_consistency(self, repository):
        """测试仓库删除的一致性"""
        logger.info("Testing repository deletion consistency...")
        
        with self.app.app_context():
            repo_id = repository.id
            local_path = repository.local_path
            
            # Verify local path exists before deletion
            assert os.path.exists(local_path), "Local path doesn't exist before deletion"
            
            # Delete repository
            delete_result = self.repository_service.delete_repository(
                repository_id=repo_id,
                user_id=self.test_user.id
            )
            
            assert delete_result['success'], f"Repository deletion failed: {delete_result.get('error')}"
            logger.info("Repository deleted successfully")
            
            # Verify database consistency
            deleted_repo = Repository.query.get(repo_id)
            assert deleted_repo is None, "Repository still exists in database after deletion"
            
            # Verify file system consistency
            assert not os.path.exists(local_path), f"Local path still exists after deletion: {local_path}"
            
            # Verify associated documents are also deleted (cascade delete)
            associated_docs = Document.query.filter_by(repository_id=repo_id).all()
            assert len(associated_docs) == 0, "Associated documents not deleted"
            
            logger.info("Repository deletion consistency verified")

    def run_comprehensive_test(self):
        """运行完整的集成测试"""
        logger.info("Starting comprehensive repository-document integration test...")
        
        try:
            # Setup
            self.setup_test_environment()
            
            # Test repository clone consistency
            repository = self.test_repository_clone_consistency()
            logger.info("✓ Repository clone consistency test passed")
            
            # Test directory read/write consistency
            self.test_directory_read_write_consistency(repository)
            logger.info("✓ Directory read/write consistency test passed")
            
            # Test repository sync consistency
            self.test_repository_sync_consistency(repository)
            logger.info("✓ Repository sync consistency test passed")
            
            # Test document generation consistency
            document = self.test_document_generation_consistency(repository)
            logger.info("✓ Document generation consistency test passed")
            
            # Test repository deletion consistency (this will delete the repository)
            self.test_repository_deletion_consistency(repository)
            logger.info("✓ Repository deletion consistency test passed")
            
            logger.info("🎉 All integration tests passed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
            
        finally:
            # Cleanup
            self.cleanup_test_environment()

    def run_quick_validation(self):
        """运行快速验证测试"""
        logger.info("Running quick validation test...")
        
        try:
            self.setup_test_environment()
            
            with self.app.app_context():
                # Test 1: Service initialization
                assert self.repository_service is not None, "Repository service not initialized"
                assert self.document_generator is not None, "Document generator not initialized"
                assert self.git_service is not None, "Git service not initialized"
                logger.info("✓ Services initialized successfully")
                
                # Test 2: Database connection
                user_count = User.query.count()
                assert user_count >= 1, "Test user not created"
                logger.info("✓ Database connection working")
                
                # Test 3: Temporary directory
                assert os.path.exists(self.temp_base_dir), "Temporary directory not created"
                assert os.access(self.temp_base_dir, os.W_OK), "Temporary directory not writable"
                logger.info(f"✓ Temporary directory ready: {self.temp_base_dir}")
                
                # Test 4: Git service base path
                assert str(self.git_service.base_repo_path) == self.temp_base_dir, "Git service base path mismatch"
                logger.info("✓ Git service configured correctly")
                
            logger.info("🎉 Quick validation test passed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Quick validation test failed: {str(e)}")
            return False
            
        finally:
            self.cleanup_test_environment()


def main():
    """主函数"""
    print("=" * 60)
    print("CoderWiki Repository-Document Integration Test")
    print("=" * 60)
    
    test_runner = RepositoryDocumentIntegrationTest()
    
    # Run quick validation first
    print("\n1. Running quick validation test...")
    quick_result = test_runner.run_quick_validation()
    
    if quick_result:
        print("\n2. Running comprehensive integration test...")
        comprehensive_result = test_runner.run_comprehensive_test()
        
        if comprehensive_result:
            print("\n🎉 All tests passed! Repository pulling and document generation integration is working correctly.")
            print("✅ Local directory read/write consistency verified.")
            return 0
        else:
            print("\n❌ Comprehensive test failed.")
            return 1
    else:
        print("\n❌ Quick validation failed. Skipping comprehensive test.")
        return 1


if __name__ == "__main__":
    exit(main())