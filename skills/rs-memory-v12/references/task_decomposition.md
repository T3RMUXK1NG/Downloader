# RS Task Decomposition — Hyper Project Management

Break ultra-complex requests into atomic, executable tasks with dependencies and parallelization.

---

## DECOMPOSITION FRAMEWORK

### Level 1: Request Analysis

When RS makes a complex request, analyze:

1. **Scope**: What's included? What's NOT included?
2. **Complexity**: How many components? How many integrations?
3. **Dependencies**: What must be built first?
4. **Deliverables**: What does RS actually need?

### Level 2: Atomic Task Breaking

Break each component into smallest executable units:

```
PROJECT: [Name]
══════════════════

COMPONENT: [Name]
├── Task A.1: [Smallest unit] → Output: [File/Feature]
├── Task A.2: [Smallest unit] → Output: [File/Feature]
└── Task A.3: [Smallest unit] → Output: [File/Feature]

COMPONENT: [Name]
├── Task B.1: [Smallest unit] → Output: [File/Feature]
├── Task B.2: [Smallest unit] → Output: [File/Feature]
└── Task B.3: [Smallest unit] → Output: [File/Feature]
```

### Level 3: Dependency Mapping

Create execution graph with dependencies:

```python
# Dependency Map
dependencies = {
    "task_1_1": [],
    "task_1_2": [],
    "task_1_3": [],
    "task_2_1": ["task_1_1", "task_1_2"],
    "task_2_2": ["task_1_2", "task_1_3"],
    "task_3_1": ["task_2_1", "task_2_2"],
}
```

---

## EXECUTION GRAPH TEMPLATE

```
EXECUTION GRAPH: [Project Name]
═══════════════════════════════

STAGE 1: FOUNDATION (No dependencies)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    Task 1.1     │  │    Task 1.2     │  │    Task 1.3     │
│   [Duration]    │  │   [Duration]    │  │   [Duration]    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
STAGE 2: CORE (Depends on Stage 1)
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    Task 2.1     │  │    Task 2.2     │  │    Task 2.3     │
│   [Duration]    │  │   [Duration]    │  │   [Duration]    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
STAGE 3: INTEGRATION (Depends on Stage 2)
                              │
                              ▼
                    ┌─────────────────┐
                    │    Task 3.1     │
                    │   [Duration]    │
                    └─────────────────┘

CRITICAL PATH: 1.1 → 2.1 → 3.1
PARALLEL TASKS: (1.1, 1.2, 1.3), (2.1, 2.3)
TOTAL ESTIMATED TIME: [Sum]
```

---

## PROJECT TYPE TEMPLATES

### Type 1: Single Tool Project

```
STAGE 1: CORE
├── Task 1.1: Core functionality
├── Task 1.2: Input handling
└── Task 1.3: Output formatting

STAGE 2: FEATURES
├── Task 2.1: Advanced features
├── Task 2.2: Error handling
└── Task 2.3: CLI interface

STAGE 3: POLISH
├── Task 3.1: Documentation
├── Task 3.2: Testing
└── Task 3.3: Integration points
```

### Type 2: Multi-Module Suite

```
STAGE 1: INFRASTRUCTURE
├── Task 1.1: Core engine
├── Task 1.2: Configuration system
├── Task 1.3: Logging system
└── Task 1.4: Plugin loader

STAGE 2: MODULES (Parallel)
├── Task 2.1: Module A
├── Task 2.2: Module B
├── Task 2.3: Module C
└── Task 2.4: Module D

STAGE 3: INTEGRATION
├── Task 3.1: Module integration
├── Task 3.2: Unified reporting
└── Task 3.3: Main menu/controller

STAGE 4: FINALIZATION
├── Task 4.1: Documentation
├── Task 4.2: Testing suite
└── Task 4.3: Deployment scripts
```

### Type 3: Full Platform (Website + API + DB)

```
STAGE 1: FOUNDATION
├── Task 1.1: Database schema
├── Task 1.2: API structure
├── Task 1.3: Authentication
└── Task 1.4: Base frontend

STAGE 2: CORE FEATURES (Parallel)
├── Task 2.1: API routes
├── Task 2.2: Frontend pages
├── Task 2.3: Database operations
└── Task 2.4: Background jobs

STAGE 3: ADVANCED FEATURES
├── Task 3.1: Real-time features
├── Task 3.2: Admin panel
├── Task 3.3: User dashboard
└── Task 3.4: Analytics

STAGE 4: PRODUCTION
├── Task 4.1: Security hardening
├── Task 4.2: Performance optimization
├── Task 4.3: Deployment configuration
└── Task 4.4: Monitoring setup
```

### Type 4: Enterprise System

```
STAGE 1: ARCHITECTURE
├── Task 1.1: System design
├── Task 1.2: Infrastructure setup
├── Task 1.3: CI/CD pipeline
└── Task 1.4: Development environment

STAGE 2: MICROSERVICES (Parallel)
├── Task 2.1: Service A
├── Task 2.2: Service B
├── Task 2.3: Service C
├── Task 2.4: Service D
└── Task 2.5: API Gateway

STAGE 3: INTEGRATION
├── Task 3.1: Service mesh
├── Task 3.2: Event bus
├── Task 3.3: Shared utilities
└── Task 3.4: Cross-service auth

STAGE 4: OBSERVABILITY
├── Task 4.1: Logging aggregation
├── Task 4.2: Metrics collection
├── Task 4.3: Distributed tracing
└── Task 4.4: Alerting

STAGE 5: PRODUCTION
├── Task 5.1: Load testing
├── Task 5.2: Security audit
├── Task 5.3: Documentation
└── Task 5.4: Deployment
```

---

## PROGRESS TRACKING

### Task Status Tracking

```python
class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class Task:
    def __init__(self, id, description, dependencies=[]):
        self.id = id
        self.description = description
        self.dependencies = dependencies
        self.status = TaskStatus.PENDING
        self.output = None
        self.duration = None
    
    def can_start(self, completed_tasks):
        return all(dep in completed_tasks for dep in self.dependencies)
```

### Progress Report Template

```
PROJECT PROGRESS: [Name]
══════════════════════════

OVERALL: [X]% Complete

STAGE 1: FOUNDATION ████████████ 100%
├── Task 1.1 ████████████ ✓ Complete
├── Task 1.2 ████████████ ✓ Complete
└── Task 1.3 ████████████ ✓ Complete

STAGE 2: CORE      ████████░░░░  67%
├── Task 2.1 ████████████ ✓ Complete
├── Task 2.2 █████████░░░ ▶ In Progress
└── Task 2.3 ░░░░░░░░░░░░ ○ Pending

STAGE 3: FEATURES  ░░░░░░░░░░░░   0%
├── Task 3.1 ░░░░░░░░░░░░ ○ Blocked (waiting 2.2)
├── Task 3.2 ░░░░░░░░░░░░ ○ Blocked (waiting 2.3)
└── Task 3.3 ░░░░░░░░░░░░ ○ Pending

BLOCKERS:
- Task 3.1 waiting for Task 2.2

NEXT ACTIONS:
- Complete Task 2.2
- Start Task 3.1 after 2.2 completes
```

---

## PARALLEL EXECUTION

### Identifying Parallel Opportunities

Tasks that can run simultaneously:
1. **No dependencies between them**
2. **Don't share mutable state**
3. **Independent outputs**

### Parallel Execution Matrix

```
PARALLEL GROUP 1 (Foundation):
├── Task 1.1 (Research) ─────┐
├── Task 1.2 (Design) ───────┼──→ Can run simultaneously
└── Task 1.3 (Setup) ────────┘

PARALLEL GROUP 2 (Modules):
├── Task 2.1 (Module A) ─────┐
├── Task 2.2 (Module B) ─────┼──→ Can run simultaneously
├── Task 2.3 (Module C) ─────┤
└── Task 2.4 (Module D) ─────┘

SEQUENTIAL (Integration):
├── Task 3.1 (Integration) ──→ Must wait for all Group 2
└── Task 3.2 (Testing) ──────→ Must wait for 3.1
```

---

## INCREMENTAL DELIVERY

### Every Task is a Deliverable

Each task should produce something usable:

| Task | Deliverable | RS Can Use |
|------|-------------|------------|
| 1.1 | Core scanner | Basic scanning works |
| 1.2 | Output formatter | Results in JSON/CSV |
| 1.3 | CLI interface | Easy to use |
| 2.1 | Threading | Faster scanning |
| 2.2 | Progress bars | Better UX |

### Milestone Delivery

After each stage, RS gets a working piece:

```
MILESTONE 1 (After Stage 1): Basic working tool
MILESTONE 2 (After Stage 2): Feature-complete tool
MILESTONE 3 (After Stage 3): Production-ready tool
MILESTONE 4 (After Stage 4): Enterprise-grade system
```

---

## EXAMPLE DECOMPOSITION

**Request**: "Build me a complete security operations center (SOC) monitoring platform"

```
PROJECT: SOC Monitoring Platform
═════════════════════════════════

STAGE 1: FOUNDATION (Week 1)
├── Task 1.1: Database schema design
├── Task 1.2: API framework setup
├── Task 1.3: Authentication system
├── Task 1.4: Basic dashboard UI
└── Task 1.5: Configuration system
    → MILESTONE: Basic platform running

STAGE 2: DATA COLLECTION (Week 2) [PARALLEL]
├── Task 2.1: Log collector agent
├── Task 2.2: Network monitor agent
├── Task 2.3: Host monitor agent
├── Task 2.4: Cloud monitor agent
└── Task 2.5: Custom webhook receiver
    → MILESTONE: Data flowing in

STAGE 3: ANALYSIS ENGINE (Week 3)
├── Task 3.1: Rule engine
├── Task 3.2: Correlation engine
├── Task 3.3: ML anomaly detection
└── Task 3.4: Threat intelligence feed
    → MILESTONE: Alerts generating

STAGE 4: RESPONSE SYSTEM (Week 4)
├── Task 4.1: Alert management
├── Task 4.2: Incident tracking
├── Task 4.3: Automated response
├── Task 4.4: Playbook engine
└── Task 4.5: Notification system
    → MILESTONE: Full SOC capabilities

STAGE 5: VISUALIZATION (Week 5)
├── Task 5.1: Real-time dashboards
├── Task 5.2: Investigation views
├── Task 5.3: Report generation
└── Task 5.4: Mobile app basics
    → MILESTONE: Production-ready

STAGE 6: ENTERPRISE (Week 6)
├── Task 6.1: Multi-tenancy
├── Task 6.2: RBAC
├── Task 6.3: API documentation
├── Task 6.4: Deployment automation
└── Task 6.5: Monitoring the monitor
    → MILESTONE: Enterprise deployment

CRITICAL PATH: 6 weeks
PARALLEL OPPORTUNITIES: Stage 2 (all agents can be built simultaneously)
```
