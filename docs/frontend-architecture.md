# CoderWiki Frontend Architecture Document

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-08-24 | 1.0 | Initial frontend architecture document - Enhanced jQuery Architecture | Winston (Architect) |

## Template and Framework Selection

### Framework Decision
After analyzing the current system state and PRD requirements, we have chosen **Enhanced jQuery Architecture** as the frontend approach.

**Rationale:**
- Maintains compatibility with existing Flask + Bootstrap + jQuery foundation
- Enables rapid stabilization of current broken functionality
- Minimal learning curve for development team
- Suitable for the stated "简单HTML/JavaScript" requirement while adding necessary structure

**Template Foundation:**
- No external starter template
- Custom architecture built on Flask templating system
- Bootstrap 5.3.0 for UI components
- jQuery for DOM manipulation and AJAX
- Modern tooling overlay for development experience

## Frontend Tech Stack

### Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Framework | Enhanced jQuery Architecture | Custom | Structured frontend without framework complexity | Maintains existing stack, adds organization |
| UI Library | Bootstrap | 5.3.0 | Responsive UI components and layout | Already in use, provides robust modal/form systems |
| State Management | Centralized State Service | Custom | Application state coordination | Simple state management without framework overhead |
| Routing | History API + Custom Router | Native | Client-side navigation | Lightweight routing for SPA-like experience |
| Build Tool | Vite | 5.x | Modern development and bundling | Fast development, proper module handling |
| Styling | Bootstrap + CSS Modules | 5.3.0 | Component-scoped styling | Prevents style conflicts, maintains Bootstrap |
| Testing | Playwright | 1.x | End-to-end testing | Tests actual user workflows in browser |
| Component Library | Custom Bootstrap Components | Custom | Reusable UI patterns | Standardized component implementations |
| Form Handling | Bootstrap + Validation API | Native | Form processing and validation | Uses browser native APIs with Bootstrap styling |
| Animation | CSS Transitions + Animate.css | 4.x | UI animations and transitions | Lightweight animation without JS framework |
| Dev Tools | ESLint + Prettier | Latest | Code quality and formatting | Maintains code standards |
