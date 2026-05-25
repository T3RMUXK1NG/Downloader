# RS Collaboration Patterns — Multi-Agent Intelligence

Patterns for coordinating multiple specialized agents on complex projects.

---

## AGENT TYPES

### Core Agents

| Agent | Specialization | Tools | Best For |
|-------|---------------|-------|----------|
| **Researcher** | Information gathering | Web search, docs analysis | New domains, comparisons |
| **Coder** | Code generation | File write, code templates | All development |
| **Tester** | Quality assurance | Test frameworks, validators | All tools |
| **Documenter** | Documentation | Markdown, templates | Production tools |
| **Optimizer** | Performance | Profilers, refactoring | Complex tools |
| **Security** | Security review | Vulnerability scanners | Security tools |

### Specialized Agents

| Agent | Specialization | When to Use |
|-------|---------------|-------------|
| **Architect** | System design | Enterprise projects |
| **Integrator** | Ecosystem connections | Connecting tools |
| **Analyst** | Data analysis | OSINT, reports |
| **Automator** | Workflow creation | Automation projects |
| **Trainer** | Learning content | Tutorials, courses |

---

## COLLABORATION PATTERNS

### Pattern 1: Sequential Pipeline

```
REQUEST → [Researcher] → [Coder] → [Tester] → [Documenter] → OUTPUT
```

**When to use:** Well-defined projects with clear stages

**Example:** Build a new tool
1. Researcher: Find best practices, similar tools
2. Coder: Build the tool
3. Tester: Create test suite
4. Documenter: Generate documentation

### Pattern 2: Parallel Development

```
                    ┌─ [Coder A] ─┐
REQUEST → [Researcher] ─┼─ [Coder B] ─┼─ [Integrator] → OUTPUT
                    └─ [Coder C] ─┘
```

**When to use:** Multi-component projects

**Example:** Build a security suite
1. Researcher: Architecture design
2. Coders A, B, C: Build different modules in parallel
3. Integrator: Connect all modules

### Pattern 3: Review Loop

```
REQUEST → [Coder] ⇄ [Reviewer] → OUTPUT
              ↑________↓
```

**When to use:** Quality-critical projects

**Example:** Security tool development
1. Coder: Build initial version
2. Security Reviewer: Check for vulnerabilities
3. Coder: Fix issues
4. Loop until approved

### Pattern 4: Specialist Consultation

```
REQUEST → [Primary Agent] → [Specialist] → OUTPUT
                ↓_____________↑
```

**When to use:** Projects requiring specialized knowledge

**Example:** API integration
1. Primary Agent: Build core functionality
2. API Specialist: Handle specific API integration
3. Primary Agent: Complete remaining work

---

## PROJECT ASSIGNMENT MATRIX

### Single Tool Project

```
PROJECT: [Tool Name]
════════════════════

PRIMARY: Coder Agent
SUPPORT: 
├── Researcher (initial research)
├── Tester (quality assurance)
└── Documenter (final docs)

WORKFLOW:
Researcher (1h) → Coder (4h) → Tester (1h) → Documenter (30m)
```

### Multi-Module Suite

```
PROJECT: [Suite Name]
═════════════════════

LEAD: Architect Agent
TEAM:
├── Coder A (Module 1)
├── Coder B (Module 2)
├── Coder C (Module 3)
├── Integrator (Connection)
├── Tester (QA)
└── Documenter (Docs)

WORKFLOW:
Phase 1: Architect → Design
Phase 2: Coders A, B, C (parallel) → Modules
Phase 3: Integrator → Connect
Phase 4: Tester → Test
Phase 5: Documenter → Document
```

### Enterprise Platform

```
PROJECT: [Platform Name]
════════════════════════

LEAD: Architect Agent
TEAMS:
├── Backend Team
│   ├── Coder A (API)
│   ├── Coder B (Database)
│   └── Coder C (Services)
├── Frontend Team
│   ├── Coder D (UI)
│   └── Coder E (Components)
├── Security Team
│   └── Security Agent
├── DevOps Team
│   └── Automator Agent
└── Documentation Team
    └── Documenter Agent

WORKFLOW:
Week 1: Architecture & Setup
Week 2-3: Parallel Development
Week 4: Integration
Week 5: Testing & Security Review
Week 6: Documentation & Deployment
```

---

## AGENT COORDINATION

### Shared State Management

```python
class SharedState:
    """Shared state for agent coordination."""
    
    def __init__(self, project_id):
        self.project_id = project_id
        self.output_dir = f"~/.rs-tools/projects/{project_id}/"
        self.state_file = f"{self.output_dir}/state.json"
        self.artifacts = {}
    
    def save_artifact(self, agent, artifact_type, content):
        """Save agent's output as artifact."""
        path = f"{self.output_dir}/{agent}/{artifact_type}"
        write_file(path, content)
        self.artifacts[f"{agent}/{artifact_type}"] = path
    
    def load_artifact(self, agent, artifact_type):
        """Load another agent's artifact."""
        path = self.artifacts.get(f"{agent}/{artifact_type}")
        if path:
            return read_file(path)
        return None
    
    def update_status(self, agent, status):
        """Update agent's status."""
        state = self._load_state()
        state["agents"][agent] = status
        self._save_state(state)
```

### Communication Protocol

```python
class AgentMessage:
    """Message structure for agent communication."""
    
    def __init__(self, from_agent, to_agent, message_type, content):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type  # request, response, artifact, status
        self.content = content
        self.timestamp = datetime.now()
```

### Handoff Protocol

```
AGENT HANDOFF PROTOCOL
══════════════════════

FROM: [Agent A]
TO: [Agent B]
ARTIFACTS:
├── /output/agent_a/main.py
├── /output/agent_a/config.json
└── /output/agent_a/tests/

STATUS: Complete
NEXT ACTIONS:
├── Run tests
├── Fix any failures
└── Generate documentation

NOTES:
- Feature X implemented
- Known issue Y (documented)
- Performance note Z
```

---

## WORKFLOW TEMPLATES

### Template 1: Security Tool Pipeline

```yaml
workflow:
  name: "Security Tool Development"
  
  stages:
    - name: "Research"
      agent: "Researcher"
      tasks:
        - "Find similar tools"
        - "Identify best practices"
        - "Document requirements"
      output: "research_report.md"
    
    - name: "Development"
      agent: "Coder"
      input: "research_report.md"
      tasks:
        - "Implement core functionality"
        - "Add features"
        - "Handle errors"
      output: "tool.py"
    
    - name: "Testing"
      agent: "Tester"
      input: "tool.py"
      tasks:
        - "Create unit tests"
        - "Run integration tests"
        - "Document test results"
      output: "test_results.json"
    
    - name: "Documentation"
      agent: "Documenter"
      input: 
        - "tool.py"
        - "test_results.json"
      tasks:
        - "Write README"
        - "Create usage guide"
        - "Document API"
      output: "docs/"
    
    - name: "Security Review"
      agent: "Security"
      input: "tool.py"
      tasks:
        - "Check for vulnerabilities"
        - "Review input handling"
        - "Verify secure defaults"
      output: "security_report.md"
```

### Template 2: Multi-Module Suite

```yaml
workflow:
  name: "Multi-Module Suite Development"
  
  parallel_stages:
    - name: "Module Development"
      agents:
        - agent: "Coder"
          name: "Coder-A"
          task: "Build scanner module"
          output: "modules/scanner/"
        
        - agent: "Coder"
          name: "Coder-B"
          task: "Build reporter module"
          output: "modules/reporter/"
        
        - agent: "Coder"
          name: "Coder-C"
          task: "Build OSINT module"
          output: "modules/osint/"
  
  sequential_stages:
    - name: "Integration"
      agent: "Integrator"
      input: "modules/*"
      tasks:
        - "Connect all modules"
        - "Create unified interface"
        - "Handle data flow"
      output: "main.py"
    
    - name: "Testing"
      agent: "Tester"
      input: "main.py"
      tasks:
        - "Test all modules"
        - "Test integration"
        - "Performance testing"
      output: "test_results.json"
```

---

## QUALITY CHECKPOINTS

### After Each Agent

```
QUALITY CHECKPOINT: [Agent Name]
════════════════════════════════

ARTIFACTS PRODUCED:
├── [File 1] ✓
├── [File 2] ✓
└── [File 3] ✓

CHECKS:
├── Code compiles ✓
├── Tests pass ✓
├── Documentation complete ✓
└── No security issues ✓

READY FOR HANDOFF: YES/NO
BLOCKERS: [List or None]
```

### Final Delivery Check

```
FINAL QUALITY CHECK
═══════════════════

CODE QUALITY:
├── All features implemented ✓
├── Error handling complete ✓
├── Code documented ✓
└── Style consistent ✓

TESTING:
├── Unit tests pass ✓
├── Integration tests pass ✓
├── Edge cases covered ✓
└── Performance acceptable ✓

DOCUMENTATION:
├── README complete ✓
├── Installation guide ✓
├── Usage examples ✓
└── API documented ✓

SECURITY:
├── Input validation ✓
├── No hardcoded secrets ✓
├── Secure defaults ✓
└── No known vulnerabilities ✓

READY FOR DELIVERY: YES
```

---

## AGENT PROMPT TEMPLATES

### Coder Agent

```markdown
You are the CODER agent for RS's project.

PROJECT: [Name]
OBJECTIVE: [What to build]

INPUT ARTIFACTS:
- [Artifact 1]: [Description]
- [Artifact 2]: [Description]

REQUIREMENTS:
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

QUALITY STANDARDS:
- Production-ready code
- Complete error handling
- Full documentation
- Cross-platform compatible

OUTPUT:
- Save code to: [path]
- Update status in: [state file]

When complete, hand off to: [Next Agent]
```

### Tester Agent

```markdown
You are the TESTER agent for RS's project.

PROJECT: [Name]
OBJECTIVE: Test the delivered code

INPUT:
- Code location: [path]
- Requirements: [path]

TEST MATRIX:
1. Unit tests for each function
2. Integration tests for workflows
3. Edge case testing
4. Performance testing
5. Platform compatibility

OUTPUT:
- test_[module].py files
- test_results.json
- coverage_report.json

Report any failures to: [Coder Agent]
```

### Documenter Agent

```markdown
You are the DOCUMENTER agent for RS's project.

PROJECT: [Name]
OBJECTIVE: Create comprehensive documentation

INPUT:
- Code: [path]
- Tests: [path]

DOCUMENTATION SUITE:
1. README.md - Quick start, installation
2. docs/INSTALLATION.md - Detailed setup
3. docs/USAGE.md - Complete usage guide
4. docs/API.md - API reference
5. docs/EXAMPLES.md - Practical examples

STYLE:
- Clear and concise
- Include code examples
- Hindi/English mix where appropriate

OUTPUT: docs/ directory
```
