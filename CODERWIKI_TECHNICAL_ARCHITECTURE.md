# CoderWiki Documentation Generation System - Technical Architecture

**Document Version**: 1.0  
**Created**: August 25, 2025  
**Architect**: Winston - AI Technical Architect  
**Project**: CoderWiki Enhanced Documentation Generation System  

## Executive Summary

This technical architecture document outlines the design for enhancing the CoderWiki Flask application with a comprehensive documentation generation system. The solution integrates Claude Code SDK for API-key-less document generation, implements a structured file management system, and provides MkDocs integration for static site generation.

**Architectural Impact Assessment**: HIGH
- Introduces new core services and data flows
- Modifies existing repository management patterns
- Adds new storage and processing layers
- Extends API surface significantly

## 1. System Architecture Overview

### Current Architecture Analysis

The existing CoderWiki system demonstrates solid architectural foundations:

**Strengths Identified**:
- Clean service layer separation (`services/` directory)
- Proper data model abstractions (`models/`)
- RESTful API design (`api/` endpoints)
- Existing task management system (`task_service.py`)
- BMAD agent orchestration integration
- Claude Code SDK foundation already present

**Architecture Gaps to Address**:
- No structured file output management
- Missing MkDocs integration layer
- Limited directory structure for generated assets
- No Git repository local storage standardization

### Enhanced System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CoderWiki Enhanced System               │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer (Bootstrap + jQuery)                       │
│  ├── Templates (Jinja2)                                    │
│  ├── Static Assets (CSS/JS)                                │
│  └── Document Viewer Components                            │
├─────────────────────────────────────────────────────────────┤
│  API Layer (Flask REST)                                    │
│  ├── Repository Management API                             │
│  ├── Document Generation API                               │
│  ├── MkDocs Site Management API                            │
│  └── File Management API                                   │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                              │
│  ├── Enhanced Repository Service                           │
│  ├── Document Generation Service                           │
│  ├── MkDocs Integration Service                             │
│  ├── File Management Service                               │
│  └── Claude Code Orchestration Service                     │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── SQLAlchemy Models                                      │
│  ├── Repository Metadata Store                             │
│  └── Document Generation Logs                              │
├─────────────────────────────────────────────────────────────┤
│  File System Layer                                          │
│  ├── coderwiki-output-docs/                                │
│  │   ├── repos/           (Git repositories)               │
│  │   ├── ai-generate-doc/ (Generated documentation)        │
│  │   └── mkdocs-site/     (MkDocs sites)                   │
│  └── Storage Management                                     │
└─────────────────────────────────────────────────────────────┘
```

## 2. Directory Structure and File Organization

### Enhanced Project Structure

```
coderwiki/
├── backend/                          # Existing Flask application
│   ├── app/
│   │   ├── api/                      # REST API endpoints
│   │   │   ├── repositories.py       # Enhanced repository endpoints
│   │   │   ├── documents.py          # Document generation endpoints
│   │   │   ├── mkdocs.py             # MkDocs site management
│   │   │   └── files.py              # File management endpoints
│   │   ├── models/
│   │   │   ├── repository.py         # Enhanced repository model
│   │   │   ├── document.py           # Document metadata model
│   │   │   ├── mkdocs_site.py        # MkDocs site model
│   │   │   └── generation_task.py    # Generation task tracking
│   │   ├── services/
│   │   │   ├── repository_service.py # Enhanced repository service
│   │   │   ├── document_generation_service.py
│   │   │   ├── mkdocs_service.py
│   │   │   ├── file_management_service.py
│   │   │   └── claude_code_orchestrator.py
│   │   └── utils/
│   │       ├── directory_manager.py
│   │       ├── git_operations.py
│   │       └── mkdocs_builder.py
│   └── config.py                     # Enhanced configuration
├── coderwiki-output-docs/            # NEW: Structured output directory
│   ├── repos/                        # Git repository clones (代码仓库存储)
│   │   └── {repo_name}_{repo_id}/   # Individual cloned repositories
│   ├── ai-generate-doc/              # Generated documentation (文档生成服务输出)
│   │   └── {repo_name}_{repo_id}/   # Documentation per repository
│   │       ├── technical_design.md
│   │       ├── api_documentation.md
│   │       ├── architecture_guide.md
│   │       └── developer_guide.md
│   └── mkdocs-site/                  # MkDocs sites (MkDocs站点生成)
│       └── {repo_name}_{repo_id}/   # Site per repository
│           ├── mkdocs.yml
│           ├── docs/
│           └── site/                # Built static site
├── frontend/                         # Existing frontend
└── bmad-docs-generator/              # Existing BMAD system
```

### Storage Naming Conventions

**Repository Directory Pattern**: `{sanitized_repo_name}_{repository_id}`
- Example: `my-awesome-project_123`
- Ensures uniqueness and file system compatibility

**Document File Naming**: `{doc_type}_{timestamp}.md`
- Example: `technical_design_20250825_143022.md`
- Maintains version history and traceability

## 3. Claude Code SDK Integration Approach

### API-Key-Less Authentication Strategy

Based on Claude Code SDK documentation analysis, we implement multiple authentication pathways:

```python
# claude_code_orchestrator.py
class ClaudeCodeOrchestrator:
    """Enhanced Claude Code SDK orchestrator with flexible authentication"""
    
    def __init__(self):
        self.auth_methods = [
            self._try_anthropic_api_key,
            self._try_bedrock_auth,
            self._try_vertex_auth,
            self._try_workspace_auth
        ]
    
    async def initialize_client(self):
        """Initialize Claude Code client with fallback authentication"""
        for auth_method in self.auth_methods:
            try:
                client = await auth_method()
                if client:
                    return client
            except Exception as e:
                logger.warning(f"Authentication method failed: {e}")
        
        raise Exception("All authentication methods failed")
    
    def _try_anthropic_api_key(self):
        """Try standard Anthropic API key authentication"""
        if os.getenv('ANTHROPIC_API_KEY'):
            return ClaudeSDKClient(api_key=os.getenv('ANTHROPIC_API_KEY'))
        return None
    
    def _try_workspace_auth(self):
        """Try workspace-based authentication (API-key-less)"""
        workspace_id = os.getenv('CLAUDE_CODE_WORKSPACE_ID')
        if workspace_id:
            return ClaudeSDKClient(
                workspace_id=workspace_id,
                use_workspace_auth=True
            )
        return None
```

### SDK Configuration Patterns

```python
# Enhanced Claude Code service configuration
class DocumentGenerationService:
    
    async def generate_document(self, repo_path: str, doc_type: str) -> Dict[str, Any]:
        """Generate documentation using Claude Code SDK"""
        
        options = ClaudeCodeOptions(
            system_prompt=self._build_system_prompt(doc_type),
            max_turns=15,  # Allow extended interactions
            permission_mode="acceptEdits",  # Auto-accept file edits
            allowed_tools=[
                "Read", "Write", "Grep", "Bash", "Edit", 
                "MultiEdit", "Task", "WebSearch"
            ],
            add_dirs=[
                Path(repo_path).resolve(),
                Path(self.bmad_docs_path).resolve()
            ],
            cwd=Path(repo_path).resolve()
        )
        
        async with ClaudeSDKClient(options=options) as client:
            response = await self._execute_generation_workflow(
                client, repo_path, doc_type
            )
            return response
```

## 4. Git Repository Management Workflow

### Enhanced Repository Service Architecture

```python
class EnhancedRepositoryService:
    """Enhanced repository service with structured file management"""
    
    def __init__(self):
        self.base_output_dir = Path("coderwiki-output-docs")
        self.repos_dir = self.base_output_dir / "repos"
        self.docs_dir = self.base_output_dir / "ai-generate-doc"
        self.mkdocs_dir = self.base_output_dir / "mkdocs-site"
        
        # Ensure directories exist
        for directory in [self.repos_dir, self.docs_dir, self.mkdocs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def clone_repository(self, repository_id: int, url: str) -> Dict[str, Any]:
        """Clone repository with structured directory management"""
        
        repo_dir_name = self._generate_repo_directory_name(repository_id, url)
        clone_path = self.repos_dir / repo_dir_name
        
        # Perform git clone
        clone_result = await self._execute_git_clone(url, clone_path)
        
        if clone_result['success']:
            # Update repository model
            await self._update_repository_paths(repository_id, {
                'local_path': str(clone_path),
                'docs_output_path': str(self.docs_dir / repo_dir_name),
                'mkdocs_path': str(self.mkdocs_dir / repo_dir_name)
            })
            
            # Create associated directories
            (self.docs_dir / repo_dir_name).mkdir(exist_ok=True)
            (self.mkdocs_dir / repo_dir_name).mkdir(exist_ok=True)
        
        return clone_result
    
    def _generate_repo_directory_name(self, repo_id: int, url: str) -> str:
        """Generate consistent directory name for repository"""
        repo_name = self._extract_repo_name(url)
        sanitized_name = re.sub(r'[^\w\-_.]', '_', repo_name.lower())
        return f"{sanitized_name}_{repo_id}"
```

### Git Operations Integration

```python
class GitOperationsManager:
    """Centralized Git operations for repository management"""
    
    async def clone_with_analysis(self, url: str, target_path: Path) -> Dict[str, Any]:
        """Clone repository and perform initial analysis"""
        
        try:
            # Clone repository
            process = await asyncio.create_subprocess_exec(
                'git', 'clone', '--depth=1', url, str(target_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    'success': False,
                    'error': stderr.decode(),
                    'operation': 'git_clone'
                }
            
            # Analyze repository structure
            analysis = await self._analyze_repository_structure(target_path)
            
            return {
                'success': True,
                'local_path': str(target_path),
                'analysis': analysis,
                'clone_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'operation': 'clone_with_analysis'
            }
    
    async def _analyze_repository_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze cloned repository structure"""
        
        # Count files by type
        file_types = {}
        total_files = 0
        total_size = 0
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
                
                suffix = file_path.suffix.lower() or '.txt'
                file_types[suffix] = file_types.get(suffix, 0) + 1
        
        # Detect primary language
        primary_language = self._detect_primary_language(file_types)
        
        # Identify key files
        key_files = self._identify_key_files(repo_path)
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'file_types': file_types,
            'primary_language': primary_language,
            'key_files': key_files,
            'has_readme': (repo_path / 'README.md').exists() or (repo_path / 'README.rst').exists(),
            'has_license': (repo_path / 'LICENSE').exists(),
            'has_gitignore': (repo_path / '.gitignore').exists()
        }
```

## 5. Documentation Generation Pipeline

### Generation Workflow Architecture

```python
class DocumentGenerationPipeline:
    """Complete documentation generation pipeline"""
    
    def __init__(self):
        self.claude_orchestrator = ClaudeCodeOrchestrator()
        self.bmad_service = BMADSubagentService()
        self.file_manager = FileManagementService()
    
    async def generate_complete_documentation(
        self, 
        repository_id: int,
        doc_types: List[str] = None
    ) -> Dict[str, Any]:
        """Generate complete documentation suite for repository"""
        
        if doc_types is None:
            doc_types = [
                'technical_design',
                'api_documentation', 
                'architecture_guide',
                'developer_guide',
                'deployment_guide'
            ]
        
        repository = await self._get_repository(repository_id)
        if not repository:
            return {'success': False, 'error': 'Repository not found'}
        
        # Create generation task
        task = await self._create_generation_task(repository_id, doc_types)
        
        results = {}
        for doc_type in doc_types:
            try:
                # Update task progress
                await self._update_task_progress(
                    task.id, 
                    f"Generating {doc_type}",
                    (len(results) / len(doc_types)) * 100
                )
                
                # Generate document
                generation_result = await self._generate_single_document(
                    repository, doc_type, task.id
                )
                
                results[doc_type] = generation_result
                
            except Exception as e:
                logger.error(f"Error generating {doc_type}: {e}")
                results[doc_type] = {
                    'success': False,
                    'error': str(e),
                    'doc_type': doc_type
                }
        
        # Mark task complete
        await self._complete_generation_task(task.id, results)
        
        return {
            'success': True,
            'task_id': task.id,
            'results': results,
            'total_documents': len([r for r in results.values() if r.get('success')])
        }
    
    async def _generate_single_document(
        self, 
        repository: Repository, 
        doc_type: str,
        task_id: int
    ) -> Dict[str, Any]:
        """Generate single document using Claude Code SDK"""
        
        # Prepare generation context
        context = {
            'repository_path': repository.local_path,
            'repository_name': repository.name,
            'repository_url': repository.url,
            'doc_type': doc_type,
            'output_path': repository.docs_output_path,
            'task_id': task_id
        }
        
        # Execute generation workflow
        result = await self.claude_orchestrator.generate_document(context)
        
        if result['success']:
            # Save document to structured location
            doc_path = await self._save_generated_document(
                result['content'], 
                repository.docs_output_path,
                doc_type
            )
            
            result['document_path'] = doc_path
            
            # Create database record
            await self._create_document_record(repository.id, doc_type, doc_path, result)
        
        return result
```

### BMAD Integration Enhancement

```python
class BMADIntegratedGenerator:
    """Enhanced BMAD integration for document generation"""
    
    async def generate_with_bmad_agents(
        self, 
        repo_path: str, 
        doc_type: str
    ) -> Dict[str, Any]:
        """Generate documentation using BMAD agent orchestration"""
        
        # Define agent workflow for document type
        workflow = self._get_bmad_workflow(doc_type)
        
        # Execute BMAD workflow
        bmad_results = await self._execute_bmad_workflow(repo_path, workflow)
        
        # Integrate BMAD results with Claude Code generation
        claude_prompt = self._build_enhanced_prompt(doc_type, bmad_results)
        
        # Execute Claude Code generation with BMAD context
        claude_result = await self.claude_orchestrator.generate_with_context(
            repo_path, claude_prompt, bmad_results
        )
        
        return {
            'success': True,
            'bmad_analysis': bmad_results,
            'claude_generation': claude_result,
            'integrated_document': claude_result.get('content', '')
        }
```

## 6. MkDocs Integration and Site Generation

### MkDocs Service Architecture

```python
class MkDocsService:
    """MkDocs integration service for static site generation"""
    
    def __init__(self):
        self.mkdocs_template_config = {
            'site_name': '',
            'theme': {
                'name': 'material',
                'features': [
                    'navigation.tabs',
                    'navigation.sections',
                    'toc.integrate',
                    'search.suggest'
                ]
            },
            'markdown_extensions': [
                'codehilite',
                'admonition',
                'toc',
                'pymdownx.superfences',
                'pymdownx.tabbed'
            ],
            'nav': []
        }
    
    async def create_mkdocs_site(self, repository_id: int) -> Dict[str, Any]:
        """Create MkDocs site from generated documentation"""
        
        repository = await self._get_repository(repository_id)
        if not repository:
            return {'success': False, 'error': 'Repository not found'}
        
        mkdocs_path = Path(repository.mkdocs_path)
        docs_path = Path(repository.docs_output_path)
        
        # Create MkDocs structure
        site_structure = await self._create_site_structure(mkdocs_path, docs_path)
        
        # Generate mkdocs.yml
        config = await self._generate_mkdocs_config(repository, site_structure)
        
        # Write configuration
        config_path = mkdocs_path / 'mkdocs.yml'
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Copy documentation files
        await self._copy_documentation_files(docs_path, mkdocs_path / 'docs')
        
        # Build site
        build_result = await self._build_mkdocs_site(mkdocs_path)
        
        if build_result['success']:
            # Create or update MkDocs site record
            await self._create_mkdocs_site_record(repository_id, {
                'config_path': str(config_path),
                'site_path': str(mkdocs_path / 'site'),
                'build_timestamp': datetime.utcnow(),
                'nav_structure': site_structure
            })
        
        return build_result
    
    async def _build_mkdocs_site(self, mkdocs_path: Path) -> Dict[str, Any]:
        """Build MkDocs site using subprocess"""
        
        try:
            process = await asyncio.create_subprocess_exec(
                'mkdocs', 'build', '--clean',
                cwd=mkdocs_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    'success': True,
                    'site_path': str(mkdocs_path / 'site'),
                    'build_log': stdout.decode()
                }
            else:
                return {
                    'success': False,
                    'error': stderr.decode(),
                    'build_log': stdout.decode()
                }
                
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'MkDocs not installed. Please install: pip install mkdocs mkdocs-material'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_mkdocs_config(
        self, 
        repository: Repository, 
        site_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate MkDocs configuration"""
        
        config = self.mkdocs_template_config.copy()
        config['site_name'] = f"{repository.name} Documentation"
        config['site_description'] = f"Generated documentation for {repository.name}"
        config['repo_url'] = repository.url
        config['nav'] = site_structure['navigation']
        
        return config
```

### Auto Site Generation Workflow

```python
class AutoSiteBuilder:
    """Automated site building workflow"""
    
    async def auto_build_pipeline(self, repository_id: int) -> Dict[str, Any]:
        """Complete automated site building pipeline"""
        
        steps = [
            ("Generating Documentation", self._generate_documentation),
            ("Creating MkDocs Site", self._create_mkdocs_site),
            ("Building Static Site", self._build_static_site),
            ("Configuring Web Server", self._configure_web_access)
        ]
        
        results = {}
        for step_name, step_func in steps:
            logger.info(f"Executing: {step_name}")
            try:
                step_result = await step_func(repository_id)
                results[step_name] = step_result
                
                if not step_result.get('success', False):
                    break
                    
            except Exception as e:
                results[step_name] = {
                    'success': False,
                    'error': str(e)
                }
                break
        
        return {
            'success': all(r.get('success', False) for r in results.values()),
            'steps': results,
            'repository_id': repository_id
        }
```

## 7. Service Layer Design

### Service Architecture Principles

**Pattern Adherence Checklist**:
- ✅ Single Responsibility: Each service handles one domain
- ✅ Dependency Inversion: Services depend on abstractions
- ✅ Interface Segregation: Focused service interfaces
- ✅ Open/Closed: Extensible service design
- ✅ Liskov Substitution: Proper inheritance hierarchies

### Enhanced Service Layer Structure

```python
# Abstract base service
class BaseService(ABC):
    """Abstract base service with common functionality"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize_dependencies()
    
    @abstractmethod
    def _initialize_dependencies(self):
        """Initialize service-specific dependencies"""
        pass
    
    async def execute_with_retry(
        self, 
        operation: Callable, 
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Execute operation with retry logic"""
        for attempt in range(max_retries):
            try:
                result = await operation()
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

# File Management Service
class FileManagementService(BaseService):
    """Service for structured file operations"""
    
    def _initialize_dependencies(self):
        self.base_path = Path("coderwiki-output-docs")
        self.storage_manager = StorageManager(self.base_path)
    
    async def create_repository_structure(
        self, 
        repository_id: int, 
        repo_name: str
    ) -> Dict[str, Any]:
        """Create complete directory structure for repository"""
        
        dir_name = self._sanitize_directory_name(repo_name, repository_id)
        
        paths = {
            'repo_clone': self.base_path / "repos" / dir_name,
            'generated_docs': self.base_path / "ai-generate-doc" / dir_name,
            'mkdocs_site': self.base_path / "mkdocs-site" / dir_name
        }
        
        # Create all directories
        for path_type, path in paths.items():
            path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created {path_type}: {path}")
        
        return {
            'success': True,
            'paths': {k: str(v) for k, v in paths.items()},
            'repository_id': repository_id
        }
    
    def _sanitize_directory_name(self, repo_name: str, repo_id: int) -> str:
        """Create safe directory name"""
        safe_name = re.sub(r'[^\w\-_.]', '_', repo_name.lower())
        return f"{safe_name}_{repo_id}"

# Document Generation Orchestrator
class DocumentGenerationOrchestrator(BaseService):
    """Orchestrates document generation across multiple services"""
    
    def _initialize_dependencies(self):
        self.claude_service = ClaudeCodeOrchestrator()
        self.bmad_service = BMADSubagentService()
        self.file_service = FileManagementService()
        self.task_service = TaskService()
    
    async def generate_documentation_suite(
        self, 
        repository_id: int,
        generation_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate complete documentation suite"""
        
        # Create generation task
        task = await self.task_service.create_task(
            repository_id=repository_id,
            task_type='documentation_generation',
            description='Generating complete documentation suite'
        )
        
        try:
            # Execute generation pipeline
            result = await self._execute_generation_pipeline(
                repository_id, generation_options, task.id
            )
            
            # Mark task complete
            await self.task_service.complete_task(task.id, result)
            
            return result
            
        except Exception as e:
            await self.task_service.fail_task(task.id, str(e))
            raise
```

## 8. API Endpoints Design

### RESTful API Architecture

```python
# Enhanced Repository API
@api.route('/repositories', methods=['POST'])
@login_required
async def create_repository():
    """Create new repository with structured setup"""
    data = request.get_json()
    
    # Validate input
    validation_result = validate_repository_data(data)
    if not validation_result['valid']:
        return jsonify({
            'success': False,
            'errors': validation_result['errors']
        }), 400
    
    try:
        # Create repository record
        repository = await repository_service.create_repository(
            user_id=current_user.id,
            url=data['url'],
            name=data.get('name'),
            description=data.get('description')
        )
        
        if repository['success']:
            # Create file structure
            file_structure = await file_service.create_repository_structure(
                repository['repository_id'],
                repository.get('name', 'unnamed-repo')
            )
            
            # Start cloning process
            clone_task = await repository_service.start_clone_process(
                repository['repository_id']
            )
            
            return jsonify({
                'success': True,
                'repository': repository,
                'file_structure': file_structure,
                'clone_task': clone_task
            })
        else:
            return jsonify(repository), 400
            
    except Exception as e:
        logger.error(f"Error creating repository: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Document Generation API
@api.route('/repositories/<int:repository_id>/generate-docs', methods=['POST'])
@login_required
async def generate_documentation(repository_id):
    """Generate documentation for repository"""
    data = request.get_json() or {}
    
    try:
        # Validate repository access
        repository = await repository_service.get_repository_by_id(
            repository_id, current_user.id
        )
        if not repository:
            return jsonify({
                'success': False,
                'error': 'Repository not found'
            }), 404
        
        # Start generation process
        generation_result = await doc_generation_service.generate_documentation_suite(
            repository_id=repository_id,
            doc_types=data.get('doc_types', ['technical_design']),
            options=data.get('options', {})
        )
        
        return jsonify(generation_result)
        
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        return jsonify({
            'success': False,
            'error': 'Generation failed'
        }), 500

# MkDocs Site API
@api.route('/repositories/<int:repository_id>/mkdocs-site', methods=['POST'])
@login_required
async def create_mkdocs_site(repository_id):
    """Create MkDocs site for repository"""
    try:
        site_result = await mkdocs_service.create_mkdocs_site(repository_id)
        return jsonify(site_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/repositories/<int:repository_id>/mkdocs-site', methods=['GET'])
@login_required
async def get_mkdocs_site(repository_id):
    """Get MkDocs site information"""
    try:
        site_info = await mkdocs_service.get_site_info(repository_id)
        return jsonify(site_info)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# File Management API
@api.route('/files/browse/<int:repository_id>')
@login_required
async def browse_repository_files(repository_id):
    """Browse repository file structure"""
    try:
        file_tree = await file_service.get_repository_file_tree(repository_id)
        return jsonify(file_tree)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

## 9. Database Schema Extensions

### New Models Required

```python
# Enhanced Repository Model
class Repository(db.Model):
    # ... existing fields ...
    
    # New fields for enhanced functionality
    docs_output_path = db.Column(db.String(1000))  # ai-generate-doc path
    mkdocs_path = db.Column(db.String(1000))       # mkdocs-site path
    auto_generate_docs = db.Column(db.Boolean, default=True)
    doc_generation_config = db.Column(db.JSON)     # Generation preferences
    last_doc_generation = db.Column(db.DateTime)
    docs_generation_status = db.Column(db.Enum(
        'never_generated', 'generating', 'completed', 'failed'
    ), default='never_generated')

# MkDocs Site Model
class MkDocsSite(db.Model):
    """MkDocs site metadata"""
    __tablename__ = 'mkdocs_sites'
    
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    site_name = db.Column(db.String(255), nullable=False)
    config_path = db.Column(db.String(1000), nullable=False)
    site_path = db.Column(db.String(1000), nullable=False)
    build_status = db.Column(db.Enum(
        'not_built', 'building', 'built', 'failed'
    ), default='not_built')
    build_error = db.Column(db.Text)
    last_built_at = db.Column(db.DateTime)
    nav_structure = db.Column(db.JSON)
    theme_config = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = db.relationship('Repository', backref='mkdocs_sites')

# Document Generation Task Model
class DocumentGenerationTask(db.Model):
    """Track document generation tasks"""
    __tablename__ = 'document_generation_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)  # 'single', 'suite', 'mkdocs'
    doc_types = db.Column(db.JSON)  # List of document types being generated
    status = db.Column(db.Enum(
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    ), default='pending')
    progress_percentage = db.Column(db.Integer, default=0)
    current_step = db.Column(db.String(255))
    generation_options = db.Column(db.JSON)
    results = db.Column(db.JSON)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    repository = db.relationship('Repository', backref='generation_tasks')

# Enhanced Document Model
class Document(db.Model):
    # ... existing fields ...
    
    # Enhanced fields
    generation_task_id = db.Column(db.Integer, db.ForeignKey('document_generation_tasks.id'))
    claude_code_session_id = db.Column(db.String(255))  # Claude Code session tracking
    bmad_analysis_results = db.Column(db.JSON)          # BMAD agent results
    generation_metadata = db.Column(db.JSON)            # Generation context/metrics
    quality_score = db.Column(db.Float)                 # Document quality assessment
    word_count = db.Column(db.Integer)
    last_updated_by_ai = db.Column(db.DateTime)
```

### Database Migration Strategy

```python
# Migration script for enhanced schema
"""Add enhanced documentation generation support

Revision ID: enhanced_docs_v1
Revises: existing_schema
Create Date: 2025-08-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # Add new columns to repositories table
    op.add_column('repositories', sa.Column('docs_output_path', sa.String(1000)))
    op.add_column('repositories', sa.Column('mkdocs_path', sa.String(1000)))
    op.add_column('repositories', sa.Column('auto_generate_docs', sa.Boolean(), default=True))
    op.add_column('repositories', sa.Column('doc_generation_config', sa.JSON()))
    op.add_column('repositories', sa.Column('last_doc_generation', sa.DateTime()))
    op.add_column('repositories', sa.Column('docs_generation_status', 
        sa.Enum('never_generated', 'generating', 'completed', 'failed'), 
        default='never_generated'))
    
    # Create mkdocs_sites table
    op.create_table('mkdocs_sites',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('repository_id', sa.Integer(), sa.ForeignKey('repositories.id'), nullable=False),
        sa.Column('site_name', sa.String(255), nullable=False),
        sa.Column('config_path', sa.String(1000), nullable=False),
        sa.Column('site_path', sa.String(1000), nullable=False),
        sa.Column('build_status', 
            sa.Enum('not_built', 'building', 'built', 'failed'), 
            default='not_built'),
        sa.Column('build_error', sa.Text()),
        sa.Column('last_built_at', sa.DateTime()),
        sa.Column('nav_structure', sa.JSON()),
        sa.Column('theme_config', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create document_generation_tasks table
    op.create_table('document_generation_tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('repository_id', sa.Integer(), sa.ForeignKey('repositories.id'), nullable=False),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('doc_types', sa.JSON()),
        sa.Column('status', 
            sa.Enum('pending', 'processing', 'completed', 'failed', 'cancelled'),
            default='pending'),
        sa.Column('progress_percentage', sa.Integer(), default=0),
        sa.Column('current_step', sa.String(255)),
        sa.Column('generation_options', sa.JSON()),
        sa.Column('results', sa.JSON()),
        sa.Column('error_message', sa.Text()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )
```

## 10. Security Considerations

### Security Architecture Review

**High-Risk Areas Identified**:
1. File system access for repository cloning
2. Subprocess execution for git operations  
3. Claude Code SDK authentication
4. MkDocs site serving
5. User-generated content in documentation

### Security Implementation Strategy

```python
class SecurityManager:
    """Centralized security management for document generation"""
    
    def __init__(self):
        self.allowed_domains = [
            'github.com', 'gitlab.com', 'bitbucket.org'
        ]
        self.base_safe_path = Path("coderwiki-output-docs").resolve()
    
    def validate_repository_url(self, url: str) -> Dict[str, Any]:
        """Validate repository URL for security"""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check domain whitelist
            if parsed.hostname not in self.allowed_domains:
                return {
                    'valid': False,
                    'error': f'Domain {parsed.hostname} not allowed'
                }
            
            # Check for malicious patterns
            if any(pattern in url.lower() for pattern in ['../', '..\\']):
                return {
                    'valid': False,
                    'error': 'Path traversal patterns detected'
                }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'URL validation error: {str(e)}'
            }
    
    def sanitize_file_path(self, file_path: str) -> Path:
        """Sanitize file paths to prevent directory traversal"""
        path = Path(file_path).resolve()
        
        # Ensure path is within safe directory
        if not str(path).startswith(str(self.base_safe_path)):
            raise SecurityError(f"Path outside safe directory: {path}")
        
        return path
    
    async def execute_safe_subprocess(
        self, 
        command: List[str], 
        cwd: Path = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """Execute subprocess with security constraints"""
        
        # Validate command
        if not self._is_safe_command(command):
            raise SecurityError(f"Unsafe command: {' '.join(command)}")
        
        # Validate working directory
        if cwd:
            cwd = self.sanitize_file_path(str(cwd))
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._get_safe_environment()
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            return {
                'success': process.returncode == 0,
                'stdout': stdout.decode(),
                'stderr': stderr.decode(),
                'returncode': process.returncode
            }
            
        except asyncio.TimeoutError:
            process.kill()
            return {
                'success': False,
                'error': 'Process timeout',
                'returncode': -1
            }
    
    def _is_safe_command(self, command: List[str]) -> bool:
        """Check if command is safe to execute"""
        safe_commands = ['git', 'mkdocs', 'python', 'pip']
        return command[0] in safe_commands
    
    def _get_safe_environment(self) -> Dict[str, str]:
        """Get safe environment variables for subprocess"""
        safe_env = {
            'PATH': os.environ.get('PATH', ''),
            'HOME': os.environ.get('HOME', ''),
            'USER': os.environ.get('USER', ''),
            'PYTHONPATH': os.environ.get('PYTHONPATH', '')
        }
        
        # Add Claude Code environment if available
        for key in ['ANTHROPIC_API_KEY', 'CLAUDE_CODE_WORKSPACE_ID']:
            if key in os.environ:
                safe_env[key] = os.environ[key]
        
        return safe_env

# Input validation decorators
def validate_repository_access(f):
    """Decorator to validate repository access"""
    @wraps(f)
    async def wrapper(*args, **kwargs):
        repository_id = kwargs.get('repository_id')
        user_id = current_user.id
        
        repository = await repository_service.get_repository_by_id(
            repository_id, user_id
        )
        
        if not repository:
            return jsonify({
                'success': False,
                'error': 'Repository not found or access denied'
            }), 403
        
        kwargs['repository'] = repository
        return await f(*args, **kwargs)
    
    return wrapper

def sanitize_input(required_fields: List[str] = None):
    """Decorator to sanitize API input"""
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            data = request.get_json() or {}
            
            # Validate required fields
            if required_fields:
                missing = [f for f in required_fields if f not in data]
                if missing:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required fields: {missing}'
                    }), 400
            
            # Sanitize string inputs
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = html.escape(value.strip())
            
            request._cached_json = data
            return await f(*args, **kwargs)
        
        return wrapper
    return decorator
```

## 11. Performance and Scalability Aspects

### Performance Architecture Analysis

**Current Performance Bottlenecks**:
1. Synchronous repository cloning operations
2. Large repository analysis overhead
3. Claude Code SDK call latency
4. File I/O operations for document generation
5. MkDocs build process duration

### Scalability Enhancement Strategy

```python
class PerformanceOptimizer:
    """Performance optimization strategies for document generation"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.task_queue = TaskQueue()
        self.resource_monitor = ResourceMonitor()
    
    async def optimize_repository_processing(
        self, 
        repository_id: int
    ) -> Dict[str, Any]:
        """Optimize repository processing pipeline"""
        
        # Check cache first
        cache_key = f"repo_analysis_{repository_id}"
        cached_result = await self.cache_manager.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # Use resource monitoring
        with self.resource_monitor.track_operation("repo_processing"):
            # Parallel processing for large repositories
            repository = await self._get_repository(repository_id)
            
            if repository.file_count > 1000:
                result = await self._process_large_repository(repository)
            else:
                result = await self._process_standard_repository(repository)
        
        # Cache result
        await self.cache_manager.set(cache_key, result, ttl=3600)
        
        return result
    
    async def _process_large_repository(
        self, 
        repository: Repository
    ) -> Dict[str, Any]:
        """Optimized processing for large repositories"""
        
        # Break into smaller chunks
        chunks = await self._create_repository_chunks(repository)
        
        # Process chunks in parallel
        chunk_results = await asyncio.gather(
            *[self._process_chunk(chunk) for chunk in chunks],
            return_exceptions=True
        )
        
        # Aggregate results
        return self._aggregate_chunk_results(chunk_results)
    
    async def optimize_claude_code_calls(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize Claude Code SDK calls"""
        
        # Pre-process repository for optimal Claude Code performance
        optimized_context = await self._prepare_optimized_context(context)
        
        # Use connection pooling
        async with self.claude_connection_pool.get_connection() as client:
            # Batch multiple operations
            if optimized_context.get('batch_operations'):
                return await self._execute_batch_operations(client, optimized_context)
            else:
                return await self._execute_single_operation(client, optimized_context)

# Async Task Processing
class AsyncTaskProcessor:
    """Asynchronous task processing for scalability"""
    
    def __init__(self):
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent tasks
        self.task_results = {}
    
    async def process_generation_tasks(
        self, 
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process multiple generation tasks asynchronously"""
        
        async def process_single_task(task):
            async with self.semaphore:
                return await self._execute_generation_task(task)
        
        # Execute tasks with concurrency control
        results = await asyncio.gather(
            *[process_single_task(task) for task in tasks],
            return_exceptions=True
        )
        
        return {
            'success': True,
            'completed_tasks': len([r for r in results if not isinstance(r, Exception)]),
            'failed_tasks': len([r for r in results if isinstance(r, Exception)]),
            'results': results
        }

# Caching Strategy
class CacheManager:
    """Intelligent caching for performance optimization"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
    
    async def cache_repository_analysis(
        self, 
        repository_id: int, 
        analysis_result: Dict[str, Any]
    ):
        """Cache repository analysis results"""
        cache_key = f"repo_analysis_{repository_id}"
        
        await self.redis_client.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(analysis_result)
        )
    
    async def cache_generated_document(
        self, 
        doc_key: str, 
        document_content: str,
        metadata: Dict[str, Any]
    ):
        """Cache generated document with metadata"""
        cache_data = {
            'content': document_content,
            'metadata': metadata,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        await self.redis_client.setex(
            f"doc_{doc_key}",
            7200,  # 2 hours TTL for documents
            json.dumps(cache_data)
        )
```

### Scalability Metrics and Monitoring

```python
class ScalabilityMonitor:
    """Monitor system scalability metrics"""
    
    def __init__(self):
        self.metrics = {
            'concurrent_generations': 0,
            'avg_generation_time': 0,
            'repository_processing_rate': 0,
            'cache_hit_rate': 0,
            'error_rate': 0
        }
    
    async def track_generation_performance(
        self, 
        repository_id: int, 
        doc_type: str
    ) -> ContextManager:
        """Context manager for tracking generation performance"""
        return GenerationPerformanceTracker(repository_id, doc_type, self)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            'current_metrics': self.metrics,
            'recommendations': self._generate_recommendations(),
            'scalability_status': self._assess_scalability()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if self.metrics['avg_generation_time'] > 300:  # 5 minutes
            recommendations.append("Consider implementing parallel document generation")
        
        if self.metrics['cache_hit_rate'] < 0.3:
            recommendations.append("Improve caching strategy for better performance")
        
        if self.metrics['error_rate'] > 0.05:
            recommendations.append("Investigate error patterns to improve reliability")
        
        return recommendations
```

## 12. Implementation Phases

### Phase-Based Implementation Strategy

**Phase 1: Foundation (Weeks 1-2)**
- Directory structure setup
- Enhanced repository service implementation
- File management service development
- Database schema extensions
- Basic Claude Code SDK integration

**Phase 2: Core Generation (Weeks 3-4)**
- Document generation pipeline implementation
- BMAD integration enhancement
- Task management system updates
- Basic API endpoints
- Security framework implementation

**Phase 3: MkDocs Integration (Weeks 5-6)**
- MkDocs service development
- Site generation workflow
- Template system implementation
- Web serving configuration
- Auto-build pipeline

**Phase 4: Performance & Polish (Weeks 7-8)**
- Performance optimization implementation
- Caching system deployment
- Comprehensive testing
- Error handling refinement
- Documentation completion

### Implementation Roadmap

```python
class ImplementationPhaseManager:
    """Manage implementation phases with dependency tracking"""
    
    def __init__(self):
        self.phases = {
            'foundation': {
                'tasks': [
                    'setup_directory_structure',
                    'implement_file_management_service',
                    'enhance_repository_service',
                    'create_database_migrations',
                    'setup_claude_code_integration'
                ],
                'dependencies': [],
                'estimated_hours': 80
            },
            'core_generation': {
                'tasks': [
                    'implement_document_generation_pipeline',
                    'enhance_bmad_integration',
                    'update_task_management_system',
                    'create_api_endpoints',
                    'implement_security_framework'
                ],
                'dependencies': ['foundation'],
                'estimated_hours': 100
            },
            'mkdocs_integration': {
                'tasks': [
                    'implement_mkdocs_service',
                    'create_site_generation_workflow',
                    'setup_template_system',
                    'configure_web_serving',
                    'implement_auto_build_pipeline'
                ],
                'dependencies': ['core_generation'],
                'estimated_hours': 80
            },
            'performance_polish': {
                'tasks': [
                    'implement_performance_optimizations',
                    'setup_caching_system',
                    'comprehensive_testing',
                    'refine_error_handling',
                    'complete_documentation'
                ],
                'dependencies': ['mkdocs_integration'],
                'estimated_hours': 60
            }
        }
    
    def get_implementation_timeline(self) -> Dict[str, Any]:
        """Generate implementation timeline with milestones"""
        timeline = {}
        current_week = 1
        
        for phase_name, phase_info in self.phases.items():
            weeks_needed = math.ceil(phase_info['estimated_hours'] / 40)  # 40 hours per week
            
            timeline[phase_name] = {
                'start_week': current_week,
                'end_week': current_week + weeks_needed - 1,
                'duration_weeks': weeks_needed,
                'estimated_hours': phase_info['estimated_hours'],
                'tasks': phase_info['tasks'],
                'dependencies': phase_info['dependencies']
            }
            
            current_week += weeks_needed
        
        return timeline
    
    def validate_implementation_readiness(self) -> Dict[str, Any]:
        """Validate system readiness for implementation"""
        checks = {
            'existing_codebase_stability': self._check_codebase_stability(),
            'dependency_availability': self._check_dependencies(),
            'infrastructure_readiness': self._check_infrastructure(),
            'team_readiness': self._check_team_readiness()
        }
        
        all_ready = all(checks.values())
        
        return {
            'ready_for_implementation': all_ready,
            'checks': checks,
            'recommendations': self._get_readiness_recommendations(checks)
        }
```

## Architectural Decision Records (ADRs)

### ADR-001: Claude Code SDK Integration Pattern
**Decision**: Use multiple authentication fallback pattern with workspace-based API-key-less mode as primary option.
**Rationale**: Provides maximum flexibility while supporting enterprise environments without API key management overhead.
**Impact**: Low coupling to authentication method, high system adaptability.

### ADR-002: File System Organization Strategy  
**Decision**: Implement structured directory hierarchy under `coderwiki-output-docs/` with type-based separation.
**Rationale**: Clear separation of concerns, easy backup/migration, predictable file locations.
**Impact**: Medium - requires file management service layer but provides long-term maintainability.

### ADR-003: MkDocs Integration Approach
**Decision**: Generate MkDocs sites per repository with auto-build pipeline.
**Rationale**: Standard documentation format, excellent theming, searchable output.
**Impact**: Medium - adds build complexity but delivers professional documentation sites.

## Conclusion and Next Steps

This technical architecture provides a comprehensive foundation for implementing the CoderWiki enhanced documentation generation system. The design maintains architectural consistency with existing patterns while introducing necessary enhancements for structured file management, Claude Code SDK integration, and MkDocs site generation.

**Key Architectural Benefits**:
1. **Maintainable**: Clear service boundaries and responsibilities
2. **Scalable**: Async processing and caching strategies
3. **Secure**: Comprehensive security framework
4. **Extensible**: Plugin-ready architecture for future enhancements
5. **Reliable**: Robust error handling and retry mechanisms

**Recommended Immediate Actions**:
1. Review and approve this architectural design
2. Begin Phase 1 implementation with directory structure setup
3. Establish development environment with required dependencies
4. Create detailed technical specifications for each service
5. Set up monitoring and testing frameworks

The architecture balances complexity with functionality, ensuring the system can evolve while maintaining stability and performance. All design decisions prioritize long-term maintainability and architectural integrity.

---

**Document Status**: Ready for Review and Implementation
**Next Review Date**: Upon Phase 1 Completion
**Approved By**: [Pending Review]