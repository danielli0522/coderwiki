"""
Contract tests for CoderWiki API endpoints.

This package contains contract tests that validate API endpoints against
their OpenAPI specifications. Tests are designed to fail initially
(TDD approach) until the corresponding endpoints are implemented.

Test Structure:
- test_repository_discovery_api.py: Tests for POST /api/repositories/discover
- test_repository_api.py: Tests for GET /api/repositories with filtering

Each test validates:
- Request/response schemas
- HTTP status codes
- Authentication requirements
- Query parameter validation
- Error responses
"""