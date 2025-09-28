
# Implementation Plan: 代码质量分析模块增强

**Branch**: `001-coderwiki-output-docs` | **Date**: 2025-09-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-coderwiki-output-docs/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
扩展现有代码质量分析模块，支持读取和分析 `coderwiki-output-docs/repos/` 目录下的本地代码仓库。增强功能包括：目录扫描、仓库发现、来源标识、分析结果统一展示，同时保持对现有Git仓库分析功能的完全兼容性。

## Technical Context
**Language/Version**: Python 3.8+ (现有CoderWiki Flask应用)
**Primary Dependencies**: Flask 2.3.3, SQLAlchemy, pathlib, 现有代码分析引擎
**Storage**: SQLite/MySQL (扩展现有Repository模型)
**Testing**: pytest (与现有测试框架一致)
**Target Platform**: Linux/macOS/Windows server (现有部署环境)
**Project Type**: web (扩展现有backend + frontend结构)
**Performance Goals**: <200ms仓库列表响应, <2s分析启动, 支持50k+文件仓库
**Constraints**: 向后兼容现有Git分析功能, 本地文件系统依赖
**Scale/Scope**: 支持数百个本地仓库, 保持现有用户体验一致性

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Code Quality Gates**:
- [x] Type hints planned for all public APIs (扩展现有Repository模型, 新增RepositoryService方法)
- [x] Security review completed (OWASP compliance - 扩展现有安全模式，无新暴露点)
- [x] Code complexity estimated within limits (≤10 cyclomatic, ≤50 line functions - 简单扩展现有类)

**Testing Gates**:
- [x] TDD approach confirmed (tests before implementation - 遵循现有TDD模式)
- [x] Coverage target ≥90% achievable with planned architecture (扩展现有测试套件)
- [x] Performance test strategy defined for repository processing features (复用现有分析引擎测试)

**UX Consistency Gates**:
- [x] Bootstrap 5 design system usage confirmed (使用现有组件库添加来源标识)
- [x] WCAG 2.1 AA accessibility requirements addressed (保持现有无障碍标准)
- [x] Responsive design approach (320px+ support) planned (复用现有响应式布局)

**Performance Gates**:
- [x] API response time targets defined (<200ms data, <2s generation - 使用现有性能基准)
- [x] Repository analysis scalability addressed (50k+ files - 复用现有大型仓库优化器)
- [x] Memory usage limits considered (<500MB per session - 保持现有内存管理模式)

## Project Structure

### Documentation (this feature)
```
specs/001-coderwiki-output-docs/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── app/
│   ├── models/
│   │   └── repository.py          # 扩展Repository模型(新增source_type, local_source_path字段)
│   ├── services/
│   │   ├── repository_service.py  # 新增discover_output_repositories()方法
│   │   └── analysis_service.py    # 修改支持本地路径分析
│   ├── api/
│   │   ├── repository.py          # 新增本地仓库发现API端点
│   │   └── analysis.py            # 确保支持本地仓库分析
│   └── utils/
│       └── code_analysis_engine.py # 确保路径兼容性
└── tests/
    ├── unit/
    │   ├── test_repository_model.py      # 测试新增字段和方法
    │   ├── test_repository_service.py    # 测试目录扫描功能
    │   └── test_analysis_service.py      # 测试本地路径分析
    ├── integration/
    │   ├── test_local_repo_discovery.py  # 集成测试：目录扫描
    │   └── test_local_repo_analysis.py   # 集成测试：本地仓库分析
    └── contract/
        └── test_repository_api.py        # API合同测试

frontend/
├── templates/
│   └── repository/
│       └── index.html             # 添加来源类型显示和刷新按钮
└── static/
    ├── css/
    │   └── repository.css         # 来源标识样式
    └── js/
        └── repository.js          # 刷新功能实现
```

**Structure Decision**: Web应用架构 - 扩展现有backend/frontend结构，主要修改Repository相关组件以支持本地仓库功能。保持现有目录结构，最小化架构变更。

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (无需记录 - 无违规)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
