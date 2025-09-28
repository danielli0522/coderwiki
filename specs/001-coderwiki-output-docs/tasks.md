# Tasks: 代码质量分析模块增强

**Input**: Design documents from `/specs/001-coderwiki-output-docs/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: Python 3.8+, Flask 2.3.3, SQLAlchemy, pathlib
2. Load design documents:
   → data-model.md: Repository entity extensions
   → contracts/: repository-discovery-api.yaml
   → quickstart.md: validation scenarios
3. Generate tasks by category:
   → Setup: dependencies, database migration
   → Tests: contract tests, integration tests
   → Core: repository model, services, API endpoints
   → Integration: path handling, analysis engine
   → Polish: frontend, performance, validation
4. Apply TDD rules: Tests before implementation
5. Mark parallel tasks [P] for different files
6. Number tasks T001-T023
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `backend/app/` for models, services, api
- **Tests**: `backend/tests/` for unit, integration, contract tests
- **Frontend**: `frontend/` for templates and static files

## Phase 3.1: Setup
- [ ] T001 Create database migration script for Repository model extensions in backend/database/migrations/
- [ ] T002 [P] Configure testing environment with pytest fixtures for local repository scenarios in backend/tests/conftest.py
- [ ] T003 [P] Set up mock directory structure for testing in backend/tests/fixtures/

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Contract test POST /api/repositories/discover in backend/tests/contract/test_repository_discovery_api.py
- [ ] T005 [P] Contract test GET /api/repositories with source_type filter in backend/tests/contract/test_repository_api.py
- [ ] T006 [P] Integration test local repository discovery workflow in backend/tests/integration/test_local_repo_discovery.py
- [ ] T007 [P] Integration test local repository analysis workflow in backend/tests/integration/test_local_repo_analysis.py
- [ ] T008 [P] Unit test Repository model extensions in backend/tests/unit/test_repository_model.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T009 [P] Extend Repository model with source_type and local_source_path fields in backend/app/models/repository.py
- [ ] T010 [P] Add Repository.get_analysis_path() method in backend/app/models/repository.py
- [ ] T011 [P] Add Repository.is_ready_for_analysis() method update in backend/app/models/repository.py
- [ ] T012 [P] Add Repository.create_local_repository() static method in backend/app/models/repository.py
- [ ] T013 Add discover_output_repositories() method in backend/app/services/repository_service.py
- [ ] T014 Add _is_valid_repository_directory() helper method in backend/app/services/repository_service.py
- [ ] T015 Add _analyze_local_repository() helper method in backend/app/services/repository_service.py
- [ ] T016 Update AnalysisService.start_analysis() to support local paths in backend/app/services/analysis_service.py

## Phase 3.4: API Implementation
- [ ] T017 Add POST /api/repositories/discover endpoint in backend/app/api/repository.py
- [ ] T018 Update GET /api/repositories to support source_type filtering in backend/app/api/repository.py
- [ ] T019 Update repository list response format with source fields in backend/app/api/repository.py

## Phase 3.5: Frontend Implementation
- [ ] T020 [P] Add source type display column to repository list in frontend/templates/repository/index.html
- [ ] T021 [P] Add refresh button for local repository discovery in frontend/templates/repository/index.html
- [ ] T022 [P] Add source type filter dropdown in frontend/templates/repository/index.html
- [ ] T023 [P] Implement refresh functionality in frontend/static/js/repository.js

## Phase 3.6: Integration & Validation
- [ ] T024 Run database migration and verify schema changes
- [ ] T025 Execute quickstart validation scenarios from quickstart.md
- [ ] T026 [P] Performance test: repository list response time <200ms in backend/tests/performance/test_repository_performance.py
- [ ] T027 [P] Performance test: discovery operation time in backend/tests/performance/test_discovery_performance.py
- [ ] T028 [P] End-to-end test: complete user workflow in backend/tests/e2e/test_local_repo_workflow.py

## Dependencies
- Setup (T001-T003) before everything
- Tests (T004-T008) before implementation (T009-T028)
- Repository model changes (T009-T012) before service changes (T013-T016)
- Service changes (T013-T016) before API changes (T017-T019)
- Backend complete before frontend (T020-T023)
- All implementation before validation (T024-T028)

## Parallel Execution Examples

### Phase 3.2 - All contract and integration tests together:
```
Task: "Contract test POST /api/repositories/discover in backend/tests/contract/test_repository_discovery_api.py"
Task: "Contract test GET /api/repositories with source_type filter in backend/tests/contract/test_repository_api.py"
Task: "Integration test local repository discovery workflow in backend/tests/integration/test_local_repo_discovery.py"
Task: "Integration test local repository analysis workflow in backend/tests/integration/test_local_repo_analysis.py"
Task: "Unit test Repository model extensions in backend/tests/unit/test_repository_model.py"
```

### Phase 3.3 - Repository model methods (same file, sequential):
```
Task: "Extend Repository model with source_type and local_source_path fields in backend/app/models/repository.py"
# Wait for completion, then:
Task: "Add Repository.get_analysis_path() method in backend/app/models/repository.py"
Task: "Add Repository.is_ready_for_analysis() method update in backend/app/models/repository.py"
Task: "Add Repository.create_local_repository() static method in backend/app/models/repository.py"
```

### Phase 3.5 - Frontend components together:
```
Task: "Add source type display column to repository list in frontend/templates/repository/index.html"
Task: "Add refresh button for local repository discovery in frontend/templates/repository/index.html"
Task: "Add source type filter dropdown in frontend/templates/repository/index.html"
Task: "Implement refresh functionality in frontend/static/js/repository.js"
```

## Task Generation Rules Applied

1. **From Contracts**: repository-discovery-api.yaml → T004, T005, T017, T018
2. **From Data Model**: Repository entity → T008, T009-T012
3. **From User Stories**: Discovery workflow → T006, T007, T028
4. **From Quickstart**: Validation scenarios → T025, T026-T027

## Validation Checklist

- [x] All contracts have corresponding tests (T004, T005)
- [x] All entities have model tasks (T009-T012)
- [x] All tests come before implementation
- [x] Parallel tasks target different files
- [x] Each task specifies exact file path
- [x] Dependencies properly ordered (setup → tests → models → services → API → frontend → validation)

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Run database migration (T024) before validation
- Frontend tasks can run in parallel as they target different files
- Commit after each task completion