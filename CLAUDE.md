# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CoderWiki is an intelligent code documentation generation platform built with Flask that integrates Claude Code SDK and BMAD (Business Method Analysis and Design) agents to automatically generate comprehensive technical documentation for code repositories.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

### Database Operations
```bash
cd backend
python init_db.py          # Initialize database
python create_default_user.py  # Create default users
python manage_users.py list    # List all users
python manage_users.py create <username> <email> <password>  # Create user
python manage_users.py reset <username> <password>  # Reset password
```

### Running the Application
```bash
# Quick start (recommended)
./start_services.sh

# Manual start
cd backend
PORT=5001 python run.py

# With different port
PORT=5002 python run.py
```

### Testing
```bash
cd backend

# Run all tests
python -m pytest

# Run specific test types
python -m pytest tests/unit/           # Unit tests
python -m pytest tests/integration/   # Integration tests
python -m pytest tests/e2e/          # End-to-end tests

# Run with coverage
python -m pytest --cov=app --cov-report=html --cov-report=term-missing

# Run performance tests (marked as slow)
python -m pytest -m "performance"

# Skip slow tests
python -m pytest -m "not slow"
```

### Code Quality
```bash
cd backend

# Linting
flake8 app/                # Check code style
black app/                 # Format code
pylint app/               # Static analysis

# Run all quality checks
flake8 app/ && black app/ --check && pylint app/
```

## Architecture Overview

### High-Level Structure
- **Backend**: Flask application (`backend/`) with REST API
- **Frontend**: Bootstrap + jQuery templates (`frontend/`)
- **BMAD System**: AI agent orchestration (`bmad-docs-generator/`)
- **Database**: SQLite (dev) / MySQL (prod)

### Core Modules
- **User Management**: Authentication, session management
- **Repository Management**: Git repo integration, sync operations
- **Document Generation**: Claude Code SDK + BMAD agents
- **Task Management**: Async task processing, progress tracking

### Key Services
- `claude_code_service.py`: Claude Code SDK integration
- `bmad_subagent_config.py`: BMAD agent configuration
- `task_service.py`: Background task management
- `repository_service.py`: Git repository operations
- `document_generator.py`: MCP-based document generation

### BMAD Agent System
Located in `bmad-docs-generator/`, this system orchestrates AI agents:
- **Code Analyst (Alex)**: Deep codebase scanning and analysis
- **Architecture Analyst**: System architecture evaluation
- **Flow Analyst (Jordan)**: Business process documentation
- **Problem Solver (Dr. Morgan)**: Issue diagnosis and solutions
- **Doc Engineer (Maya)**: Final documentation assembly

### Database Models
- `User`: User accounts and authentication
- `Repository`: Code repositories and metadata
- `Document`: Generated documentation versions
- `Task`: Background task tracking
- `BMADAgentExecution`: Agent execution records

### Key API Endpoints
- `/api/auth/*`: Authentication (login, register, logout)
- `/api/repositories/*`: Repository management
- `/api/repositories/{id}/generate`: Smart document generation
- `/api/tasks/*`: Task status and monitoring
- `/api/claude/*`: Claude Code session management

## Configuration

### Environment Variables
Key environment variables (see `backend/env.example`):
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///coderwiki.db
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
CLAUDE_CODE_WORKSPACE_ID=your-workspace-id
```

### Config Files
- `backend/config.py`: Main application configuration
- `backend/app/config.py`: Application-specific settings
- Development config uses SQLite, production can use MySQL

### Default Users
The system creates three default accounts:
- **admin/admin123**: Administrator account
- **demo/demo123**: Demo user account  
- **testuser/test123**: Test user account

## Development Workflow

### Adding New Features
1. Create feature branch from `main`
2. Implement changes in appropriate modules
3. Add unit/integration tests
4. Run test suite and quality checks
5. Test locally with `./start_services.sh`
6. Submit PR against `main` branch

### Working with BMAD Agents
- Agent definitions: `bmad-docs-generator/agents/`
- Team configurations: `bmad-docs-generator/agent-teams/`
- Workflows: `bmad-docs-generator/workflows/`
- Templates: `bmad-docs-generator/templates/`

### Database Changes
1. Modify models in `backend/app/models/`
2. Create migration: `flask db migrate -m "description"`
3. Apply migration: `flask db upgrade`
4. Update seed data if needed

### Testing Strategy
- Unit tests for individual functions/classes
- Integration tests for API endpoints and database operations
- End-to-end tests for complete user workflows
- Performance tests for large-scale operations

### Common Issues
1. **Port 5001 in use**: Use `PORT=5002 python run.py`
2. **Database errors**: Run `python init_db.py` to reinitialize
3. **API key issues**: Run `python scripts/diagnose_api_quota.py`
4. **Missing dependencies**: Ensure virtual environment is activated

## File Organization

### Backend Structure
```
backend/app/
├── api/          # REST API endpoints
├── models/       # Database models
├── services/     # Business logic layer
├── utils/        # Utility functions and helpers
├── routes/       # Web page routes
└── static/       # Static assets
```

### Frontend Structure
```
frontend/
├── templates/    # Jinja2 HTML templates
├── static/css/   # Stylesheets
└── static/js/    # JavaScript modules
```

### Testing Structure
```
backend/tests/
├── unit/         # Unit tests
├── integration/  # Integration tests
├── e2e/          # End-to-end tests
└── conftest.py   # Test configuration
```

## Performance Considerations

- Database queries use SQLAlchemy ORM with connection pooling
- Background tasks prevent blocking the main thread
- Static files served through Flask in development
- Claude Code sessions are cached and reused when possible
- BMAD workflows run asynchronously with progress tracking

## Security Notes

- User passwords hashed with bcrypt
- SQL injection protection via SQLAlchemy
- XSS protection in templates
- CSRF protection enabled
- API keys stored in environment variables
- User data isolation by user ID