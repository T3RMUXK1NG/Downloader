# Compliance Frameworks Reference

## Supported Frameworks

### SOC 2 Type II
- **Controls**: ~100
- **Trust Service Criteria**: Security, Availability, Processing Integrity, Confidentiality, Privacy
- **Evidence Requirements**: Policies, procedures, technical controls, testing evidence

### ISO 27001
- **Controls**: 114
- **Domains**: 14
- **Control Objectives**: 35
- **Annex A Controls**: 114

### GDPR
- **Articles**: 99
- **Key Requirements**: Lawful basis, consent, data subject rights, DPO, breach notification

### PCI DSS
- **Requirements**: 12
- **Sub-requirements**: ~250
- **Levels**: 1-4 (based on transaction volume)

### HIPAA
- **Rules**: Privacy, Security, Breach Notification
- **Standards**: 18 administrative, physical, technical safeguards

### NIST 800-53
- **Controls**: 1000+
- **Families**: 20
- **Impact Levels**: Low, Moderate, High

## Compliance Engine

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class Control:
    id: str
    name: str
    description: str
    category: str
    evidence_required: List[str]
    automated_check: Optional[str]

@dataclass
class ControlResult:
    control: Control
    status: ComplianceStatus
    evidence: Dict[str, Any]
    gaps: List[str]
    remediation: List[str]

class ComplianceFramework(ABC):
    """Base compliance framework."""
    
    @abstractmethod
    def get_controls(self) -> List[Control]:
        """Get all controls."""
        pass
    
    @abstractmethod
    async def check_control(self, control: Control, scope: Dict) -> ControlResult:
        """Check a control."""
        pass

class SOC2Framework(ComplianceFramework):
    """SOC 2 compliance framework."""
    
    CONTROLS = [
        Control(
            id="CC6.1",
            name="Logical Access",
            description="Logical access to systems is restricted",
            category="Security",
            evidence_required=["Access policy", "Access logs", "MFA configuration"],
            automated_check="check_mfa_enabled"
        ),
        Control(
            id="CC6.6",
            name="Security Incidents",
            description="Security incidents are tracked and resolved",
            category="Security",
            evidence_required=["Incident response plan", "Incident log", "Resolution evidence"],
            automated_check="check_incident_tracking"
        ),
        Control(
            id="CC7.1",
            name="Vulnerability Management",
            description="Vulnerabilities are identified and remediated",
            category="Security",
            evidence_required=["Vulnerability scan reports", "Remediation records"],
            automated_check="check_vuln_scanning"
        ),
        # ... more controls
    ]
    
    def get_controls(self) -> List[Control]:
        return self.CONTROLS
    
    async def check_control(self, control: Control, scope: Dict) -> ControlResult:
        """Check SOC 2 control."""
        if control.automated_check:
            check_result = await self._run_automated_check(
                control.automated_check, scope
            )
        else:
            check_result = await self._manual_check(control, scope)
        
        return ControlResult(
            control=control,
            status=check_result['status'],
            evidence=check_result['evidence'],
            gaps=check_result.get('gaps', []),
            remediation=check_result.get('remediation', [])
        )

class ComplianceEngine:
    """Automated compliance engine."""
    
    FRAMEWORKS = {
        'soc2': SOC2Framework(),
        'iso27001': ISO27001Framework(),
        'gdpr': GDPRFramework(),
        'pci_dss': PCIDSSFramework(),
        'hipaa': HIPAAFramework(),
        'nist': NISTFramework()
    }
    
    async def assess(self, framework: str, scope: Dict) -> Dict:
        """Run compliance assessment."""
        fw = self.FRAMEWORKS[framework]
        controls = fw.get_controls()
        
        results = []
        for control in controls:
            result = await fw.check_control(control, scope)
            results.append(result)
        
        return self._compile_report(framework, results)
    
    def _compile_report(self, framework: str, results: List[ControlResult]) -> Dict:
        """Compile compliance report."""
        compliant = sum(1 for r in results if r.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for r in results if r.status == ComplianceStatus.NON_COMPLIANT)
        partial = sum(1 for r in results if r.status == ComplianceStatus.PARTIAL)
        
        return {
            'framework': framework,
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_controls': len(results),
                'compliant': compliant,
                'non_compliant': non_compliant,
                'partial': partial,
                'compliance_percentage': (compliant / len(results)) * 100
            },
            'results': [
                {
                    'control_id': r.control.id,
                    'control_name': r.control.name,
                    'status': r.status.value,
                    'gaps': r.gaps,
                    'remediation': r.remediation
                }
                for r in results
            ],
            'priority_remediation': self._prioritize_remediation(results)
        }
    
    def _prioritize_remediation(self, results: List[ControlResult]) -> List[Dict]:
        """Prioritize remediation actions."""
        priorities = []
        for r in results:
            if r.status == ComplianceStatus.NON_COMPLIANT:
                priority = self._calculate_priority(r)
                priorities.append({
                    'control': r.control.id,
                    'priority': priority,
                    'remediation': r.remediation
                })
        return sorted(priorities, key=lambda x: x['priority'], reverse=True)
```

## Compliance Report Template

```
┌──────────────────────────────────────────────────────────────┐
│  COMPLIANCE ASSESSMENT REPORT                                │
│  Framework: SOC 2 Type II                                    │
│  Date: [Generated Date]                                      │
├──────────────────────────────────────────────────────────────┤
│  OVERALL COMPLIANCE: 87% ████████████████████░░░             │
│                                                              │
│  BY TRUST SERVICE CRITERIA:                                  │
│  ├── Security: 92% ████████████████████████░░                │
│  ├── Availability: 85% █████████████████████░░░░             │
│  ├── Processing Integrity: 88% ████████████████████░░        │
│  ├── Confidentiality: 90% ██████████████████████░░           │
│  └── Privacy: 80% ████████████████████░░░░░░                 │
├──────────────────────────────────────────────────────────────┤
│  NON-COMPLIANT CONTROLS: 13                                  │
│  ├── CC6.1: Logical access not MFA-enforced                 │
│  ├── CC6.6: Security incidents not tracked                   │
│  └── CC7.1: Vulnerability scanning not automated            │
├──────────────────────────────────────────────────────────────┤
│  REMEDIATION PRIORITY:                                       │
│  1. [HIGH] Enable MFA for all systems (3 days)              │
│  2. [HIGH] Implement centralized SIEM (1 week)              │
│  3. [MEDIUM] Automate vulnerability scanning (2 weeks)      │
└──────────────────────────────────────────────────────────────┘
```

## Evidence Collection

```python
class EvidenceCollector:
    """Collect compliance evidence automatically."""
    
    def __init__(self):
        self.collectors = {
            'access_logs': AccessLogCollector(),
            'config_snapshots': ConfigSnapshotCollector(),
            'vulnerability_scans': VulnScanCollector(),
            'policy_documents': PolicyDocumentCollector()
        }
    
    async def collect_for_control(self, control: Control) -> Dict[str, Any]:
        """Collect evidence for a control."""
        evidence = {}
        
        for evidence_type in control.evidence_required:
            if evidence_type in self.collectors:
                evidence[evidence_type] = await self.collectors[evidence_type].collect()
        
        return evidence
    
    async def collect_all(self, framework: str) -> Dict[str, Any]:
        """Collect all evidence for a framework."""
        fw = ComplianceEngine.FRAMEWORKS[framework]
        controls = fw.get_controls()
        
        all_evidence = {}
        for control in controls:
            all_evidence[control.id] = await self.collect_for_control(control)
        
        return all_evidence
```
