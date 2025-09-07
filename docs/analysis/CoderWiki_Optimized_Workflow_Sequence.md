# CoderWiki Optimized Workflow - Complete Sequence Diagram

## System Overview

The CoderWiki system has been optimized to bypass the complex BMAD workflow orchestrator and directly use Claude headless mode with prompts from `docs/prompts/` directory. This sequence diagram shows the complete end-to-end workflow from repository creation to final MkDocs site generation.

## Key Optimizations

1. **Simplified Architecture**: Direct prompts + Claude headless mode (no BMAD orchestrator)
2. **Unified Directory Management**: Centralized path handling via DirectoryService
3. **Configuration-Driven**: Uses `docs/prompts/sequence.json` for execution sequence
4. **Streamlined Generation**: Three-step AI document generation process

## Complete End-to-End Sequence Diagram

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant WebUI as 🌐 Web UI
    participant API as 🔧 API Layer
    participant RepoService as 📦 Repository Service
    participant DirService as 📁 Directory Service
    participant FileSystem as 💾 File System
    participant GitClone as 🔄 Git Clone
    participant DocGenService as 📝 Document Generation Service
    participant ClaudeRunner as 🤖 Claude Headless Runner
    participant ClaudeCLI as ⚡ Claude CLI
    participant MkDocsService as 📚 MkDocs Service
    participant MkDocsBuild as 🏗️ MkDocs Build
    participant WebServer as 🌐 Web Server

    Note over User, WebServer: Phase 1: Repository Creation & Cloning

    User->>WebUI: Create Repository (name, URL)
    WebUI->>API: POST /api/repositories
    API->>RepoService: create_repository(user_id, url, name, description)

    RepoService->>DirService: create_repository_directories(name, repo_id)
    Note over DirService: Creates unified directory structure
    DirService->>FileSystem: mkdir coderwiki-output-docs/repos/{name}_{id}/
    DirService->>FileSystem: mkdir coderwiki-output-docs/ai-generate-doc/{name}_{id}/
    DirService->>FileSystem: mkdir coderwiki-output-docs/mkdocs-site/{name}_{id}/
    DirService-->>RepoService: Directory paths created

    RepoService->>GitClone: git clone {url} repos/{name}_{id}/
    GitClone->>FileSystem: Clone repository files
    GitClone-->>RepoService: Repository cloned successfully

    RepoService->>API: Repository created (ID: {repo_id})
    API->>WebUI: Repository creation result
    WebUI-->>User: Repository added successfully

    Note over User, WebServer: Phase 2: AI Document Generation (Optimized)

    User->>WebUI: Generate Documentation
    WebUI->>API: POST /api/documents/generate/{repo_id}
    API->>DocGenService: generate_docs_for_repository(repo_id)

    DocGenService->>DirService: get_repository_directory(name, repo_id)
    DirService-->>DocGenService: coderwiki-output-docs/repos/{name}_{id}/

    DocGenService->>DirService: get_ai_docs_directory(name, repo_id)
    DirService-->>DocGenService: coderwiki-output-docs/ai-generate-doc/{name}_{id}/

    DocGenService->>FileSystem: Load docs/prompts/sequence.json
    FileSystem-->>DocGenService: Prompt execution sequence config

    Note over DocGenService: Load 3 prompts from sequence.json
    DocGenService->>FileSystem: Read docs/prompts/technical-overview.md
    DocGenService->>FileSystem: Read docs/prompts/API接口分析.md
    DocGenService->>FileSystem: Read docs/prompts/模块深度考古与高频提交问题.md
    FileSystem-->>DocGenService: Prompt content loaded

    loop For each prompt in sequence
        Note over DocGenService, ClaudeCLI: Execute Prompt via Claude Headless Mode
        DocGenService->>ClaudeRunner: _execute_prompt(config, repository, repo_source_dir, output_dir)

        Note over ClaudeRunner: Replace variables in prompt
        Note over ClaudeRunner: {project_name} → repository.name
        Note over ClaudeRunner: {repository_path} → repo_source_dir

        ClaudeRunner->>ClaudeCLI: claude -p "{prompt_content}" --allowedTools "Read,Grep,Glob" --add-dir "{repo_source_dir}" --permission-mode acceptEdits --timeout 600

        Note over ClaudeCLI: Execute in repository context
        ClaudeCLI->>FileSystem: Analyze repository files (Read, Grep, Glob)
        ClaudeCLI->>ClaudeCLI: Generate documentation content
        ClaudeCLI-->>ClaudeRunner: Execution result with generated content

        ClaudeRunner->>FileSystem: Write ai-generate-doc/{name}_{id}/{name}-{prompt-name}.md
        ClaudeRunner-->>DocGenService: Generation result (success/failure, content, execution_time)
    end

    DocGenService->>API: Generation completed (3 documents created)
    API->>WebUI: AI documents generated successfully
    WebUI-->>User: Documentation generation completed

    Note over User, WebServer: Phase 3: MkDocs Site Generation

    User->>WebUI: Build Documentation Site
    WebUI->>API: POST /api/mkdocs/build/{repo_id}
    API->>MkDocsService: build_site_for_repository(repo_id, user_id)

    MkDocsService->>DirService: get_mkdocs_site_path(name, repo_id)
    DirService-->>MkDocsService: coderwiki-output-docs/mkdocs-site/{name}_{id}/

    MkDocsService->>DirService: get_mkdocs_docs_path(name, repo_id)
    DirService-->>MkDocsService: coderwiki-output-docs/mkdocs-site/{name}_{id}/docs/

    Note over MkDocsService: Collect AI-generated documents
    MkDocsService->>FileSystem: Scan ai-generate-doc/{name}_{id}/*.md
    FileSystem-->>MkDocsService: List of generated documents

    Note over MkDocsService: Create MkDocs structure
    loop For each AI document
        MkDocsService->>FileSystem: Copy {name}-{prompt}.md → mkdocs-site/{name}_{id}/docs/
    end

    MkDocsService->>FileSystem: Generate mkdocs.yml config
    Note over FileSystem: mkdocs-site/{name}_{id}/mkdocs.yml
    Note over FileSystem: - site_name: "{name} Documentation"
    Note over FileSystem: - theme: material with Mermaid support
    Note over FileSystem: - nav: Auto-generated from documents

    MkDocsService->>FileSystem: Create mermaid-init.js script
    Note over FileSystem: mkdocs-site/{name}_{id}/docs/javascripts/mermaid-init.js

    MkDocsService->>MkDocsBuild: mkdocs build --clean (cwd: mkdocs-site/{name}_{id}/)
    MkDocsBuild->>FileSystem: Generate static site files
    Note over FileSystem: mkdocs-site/{name}_{id}/site/index.html
    Note over FileSystem: mkdocs-site/{name}_{id}/site/assets/
    Note over FileSystem: mkdocs-site/{name}_{id}/site/search/
    MkDocsBuild-->>MkDocsService: Static site built successfully

    MkDocsService->>API: Site built successfully
    API->>WebUI: MkDocs site ready
    WebUI-->>User: Documentation site built: /sites/{name}_{id}/

    Note over User, WebServer: Phase 4: Documentation Access

    User->>WebServer: Access /sites/{name}_{id}/
    WebServer->>FileSystem: Serve static files from mkdocs-site/{name}_{id}/site/
    FileSystem-->>WebServer: Static HTML/CSS/JS files
    WebServer-->>User: Rendered documentation site with navigation

    Note over User, WebServer: File Storage Summary
    Note over FileSystem: coderwiki-output-docs/
    Note over FileSystem: ├── repos/{name}_{id}/           # Git cloned repository
    Note over FileSystem: ├── ai-generate-doc/{name}_{id}/ # AI generated *.md files
    Note over FileSystem: └── mkdocs-site/{name}_{id}/     # MkDocs project & built site
    Note over FileSystem:     ├── docs/                    # Source markdown files
    Note over FileSystem:     ├── mkdocs.yml               # MkDocs configuration
    Note over FileSystem:     └── site/                    # Built static site
```

## Key Components and Their Responsibilities

### 1. **DirectoryService** (Unified Path Management)

- **Location**: `/backend/app/services/directory_service.py`
- **Responsibility**: Centralized directory structure management
- **Key Methods**:
  - `get_repository_clone_path()` → `coderwiki-output-docs/repos/{name}_{id}/`
  - `get_ai_docs_path()` → `coderwiki-output-docs/ai-generate-doc/{name}_{id}/`
  - `get_mkdocs_site_path()` → `coderwiki-output-docs/mkdocs-site/{name}_{id}/`

### 2. **DocumentGenerationService** (Optimized AI Generation)

- **Location**: `/backend/app/services/document_generation_service.py`
- **Responsibility**: Direct Claude headless mode execution with prompts
- **Key Optimizations**:
  - Loads prompts directly from `docs/prompts/` directory
  - Uses `sequence.json` for execution configuration
  - Bypasses BMAD orchestrator completely
  - Direct variable replacement in prompts

### 3. **Claude Headless Runner** (AI Execution Engine)

- **Location**: `/claude_headless_runner.py`
- **Responsibility**: Execute Claude CLI in headless mode
- **Key Features**:
  - Configurable tools (Read, Grep, Glob, Bash, WebSearch)
  - Working directory context (`--add-dir`)
  - Permission modes (`acceptEdits`)
  - Timeout handling (300-1200s)

### 4. **MkDocsService** (Static Site Generation)

- **Location**: `/backend/app/services/mkdocs_service.py`
- **Responsibility**: Convert AI documents to static documentation sites
- **Key Features**:
  - Material theme with dark/light mode
  - Mermaid diagram support
  - Search functionality
  - Auto-generated navigation

## Configuration Files

### 1. **Prompt Execution Sequence** (`docs/prompts/sequence.json`)

```json
{
  "version": "1.0",
  "execution_sequence": [
    {
      "prompt_file": "technical-overview.md",
      "timeout": 600,
      "tools": ["Read", "Grep", "Glob"]
    },
    {
      "prompt_file": "API接口分析.md",
      "timeout": 900,
      "tools": ["Read", "Grep", "Bash"]
    },
    {
      "prompt_file": "模块深度考古与高频提交问题.md",
      "timeout": 1200,
      "tools": ["Read", "Grep", "Bash", "WebSearch"]
    }
  ]
}
```

### 2. **Available Prompts** (`docs/prompts/`)

- `technical-overview.md` - Comprehensive technical analysis
- `API接口分析.md` - API reverse engineering analysis
- `模块深度考古与高频提交问题.md` - Module archaeology & commit analysis

## File Storage Locations

### **Repository Files**

- **Location**: `coderwiki-output-docs/repos/{name}_{id}/`
- **Content**: Original cloned git repository
- **Purpose**: Source code analysis context for AI

### **AI Generated Documents**

- **Location**: `coderwiki-output-docs/ai-generate-doc/{name}_{id}/`
- **Content**: `{name}-{prompt-name}.md` files
- **Purpose**: AI-generated technical documentation

### **MkDocs Sites**

- **Location**: `coderwiki-output-docs/mkdocs-site/{name}_{id}/`
- **Structure**:
  - `docs/` - Source markdown files (copied from ai-generate-doc)
  - `mkdocs.yml` - MkDocs configuration
  - `site/` - Built static HTML site
  - `docs/javascripts/mermaid-init.js` - Mermaid diagram support

## Performance & Scalability Features

1. **Parallel Processing**: Multiple prompts can be executed in sequence
2. **Configurable Timeouts**: Different prompts have different complexity timeouts
3. **Tool Restrictions**: Each prompt specifies allowed tools for security
4. **Directory Isolation**: Each repository has isolated directory structure
5. **Static Site Caching**: Built sites are cached until regenerated

## System Requirements

1. **Claude CLI**: Must be installed and available in PATH
2. **MkDocs**: Python package with Material theme
3. **Git**: For repository cloning
4. **Python 3.8+**: For backend services
5. **Node.js**: For frontend (optional)

This optimized architecture provides a streamlined, maintainable, and scalable solution for automated technical documentation generation with AI assistance.
