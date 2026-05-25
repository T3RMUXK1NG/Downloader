# Cloud Dominance Engine - RS Memory Skill v11.0 ABSOLUTE DOMINION NEXUS

## Rule 94: Cloud Dominance Engine

The Cloud Dominance Engine provides multi-cloud security orchestration, container security analysis, and cloud misconfiguration detection across AWS, Azure, and GCP environments.

---

## CloudSecurityOrchestrator Class

```python
import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum


class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI = "multi"


class SeverityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ResourceType(Enum):
    EC2 = "ec2_instance"
    S3 = "s3_bucket"
    IAM = "iam_policy"
    VPC = "vpc_network"
    LAMBDA = "lambda_function"
    RDS = "rds_database"
    EKS = "eks_cluster"
    ECR = "ecr_repository"
    CLOUDFRONT = "cloudfront_distribution"
    ROUTE53 = "route53_zone"
    VM = "virtual_machine"
    BLOB = "blob_storage"
    KEYVAULT = "key_vault"
    SQL = "sql_database"
    AKS = "aks_cluster"
    COMPUTE = "compute_instance"
    GCS = "cloud_storage"
    IAM_GCP = "iam_policy"
    GKE = "gke_cluster"
    CLOUDSQL = "cloud_sql"


@dataclass
class CloudResource:
    resource_id: str
    resource_type: ResourceType
    provider: CloudProvider
    region: str
    name: str
    tags: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    misconfigurations: List[Dict] = field(default_factory=list)
    risk_score: float = 0.0


@dataclass
class Misconfiguration:
    resource_id: str
    resource_type: str
    provider: str
    rule_id: str
    severity: SeverityLevel
    category: str
    description: str
    remediation: str
    compliance_impact: List[str]
    detected_at: float = field(default_factory=time.time)


@dataclass
class SecurityScanResult:
    scan_id: str
    provider: CloudProvider
    total_resources: int
    misconfigured_resources: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    compliance_score: float
    misconfigurations: List[Misconfiguration]
    scan_duration: float
    timestamp: float = field(default_factory=time.time)


class CloudSecurityOrchestrator:
    """Multi-cloud security orchestration across AWS, Azure, and GCP."""

    def __init__(self):
        self.providers: Dict[CloudProvider, Dict] = {
            CloudProvider.AWS: {
                "authenticated": False,
                "regions": ["us-east-1", "us-west-2", "eu-west-1"],
                "resources": [],
                "scan_history": []
            },
            CloudProvider.AZURE: {
                "authenticated": False,
                "subscriptions": [],
                "resources": [],
                "scan_history": []
            },
            CloudProvider.GCP: {
                "authenticated": False,
                "projects": [],
                "resources": [],
                "scan_history": []
            }
        }
        self.all_resources: List[CloudResource] = []
        self.misconfiguration_rules: Dict[str, Dict] = {}
        self.compliance_frameworks: Dict[str, Dict] = {}
        self._initialize_rules()
        self._initialize_compliance()

    def _initialize_rules(self):
        """Initialize cloud misconfiguration detection rules."""
        self.misconfiguration_rules = {
            # AWS Rules
            "AWS-S3-001": {
                "provider": CloudProvider.AWS,
                "resource_type": ResourceType.S3,
                "severity": SeverityLevel.CRITICAL,
                "category": "data_exposure",
                "description": "S3 bucket has public read access enabled",
                "remediation": "Disable public read access on S3 bucket. Enable S3 Block Public Access at account level.",
                "compliance": ["CIS", "SOC2", "PCI-DSS", "GDPR"]
            },
            "AWS-S3-002": {
                "provider": CloudProvider.AWS,
                "resource_type": ResourceType.S3,
                "severity": SeverityLevel.HIGH,
                "category": "encryption",
                "description": "S3 bucket does not have default encryption enabled",
                "remediation": "Enable SSE-S3 or SSE-KMS default encryption on the S3 bucket.",
                "compliance": ["CIS", "SOC2", "PCI-DSS"]
            },
            "AWS-S3-003": {
                "provider": CloudProvider.AWS,
                "resource_type": ResourceType.S3,
                "severity": SeverityLevel.MEDIUM,
                "category": "logging",
                "description": "S3 bucket access logging is not enabled",
                "remediation": "Enable server access logging for the S3 bucket.",
                "compliance": ["CIS", "SOC2"]
            },
            "AWS-IAM-001": {
                "provider": CloudProvider.AWS,
                "resource_type": ResourceType.IAM,
                "severity": SeverityLevel.CRITICAL,
                "category": "access_control",
                "description": "IAM policy grants overly permissive wildcard actions",
                "remediation": "Replace wildcard (*) actions with specific actions following least privilege.",
                "compliance": ["CIS", "SOC2", "PCI-DSS", "HIPAA"]
            },
            "AWS-IAM-002": {
                "provider": CloudProvider.AWS,
                "resource_type": ResourceType.IAM,
                "severity": SeverityLevel.HIGH,
                "category": "access_control",
                "description": "IAM user has no MFA enabled",
                "remediation": "Enable MFA for all IAM users. Enforce MFA through IAM policy conditions.",
                "compliance": ["CIS", "SOC2"]
            },
            "AWS-EC2-001": {
                "provider": CloudProvider.AWS,
                "resource_type": ResourceType.EC2,
                "severity": SeverityLevel.HIGH,
                "category": "network_security",
                "description": "Security group allows inbound traffic from 0.0.0.0/0",
                "remediation": "Restrict inbound rules to specific IP ranges. Remove 0.0.0.0/0 entries.",
                "compliance": ["CIS", "PCI-DSS", "SOC2"]
            },
            "AWS-RDS-001": {
                "provider": CloudProvider.AWS,
                "resource_type": ResourceType.RDS,
                "severity": SeverityLevel.CRITICAL,
                "category": "encryption",
                "description": "RDS instance storage is not encrypted",
                "remediation": "Enable encryption for RDS instance. Create encrypted snapshot and restore.",
                "compliance": ["PCI-DSS", "HIPAA", "GDPR"]
            },
            "AWS-LAMBDA-001": {
                "provider": CloudProvider.AWS,
                "resource_type": ResourceType.LAMBDA,
                "severity": SeverityLevel.MEDIUM,
                "category": "access_control",
                "description": "Lambda function has overly permissive execution role",
                "remediation": "Scope down IAM execution role to minimum required permissions.",
                "compliance": ["CIS", "SOC2"]
            },
            # Azure Rules
            "AZ-BLOB-001": {
                "provider": CloudProvider.AZURE,
                "resource_type": ResourceType.BLOB,
                "severity": SeverityLevel.CRITICAL,
                "category": "data_exposure",
                "description": "Azure Blob Storage container has public access enabled",
                "remediation": "Disable public access on blob container. Set access tier to Private.",
                "compliance": ["CIS", "SOC2", "GDPR"]
            },
            "AZ-VM-001": {
                "provider": CloudProvider.AZURE,
                "resource_type": ResourceType.VM,
                "severity": SeverityLevel.HIGH,
                "category": "network_security",
                "description": "NSG allows unrestricted inbound access",
                "remediation": "Restrict NSG inbound rules to specific source IP ranges.",
                "compliance": ["CIS", "PCI-DSS"]
            },
            "AZ-KEYVAULT-001": {
                "provider": CloudProvider.AZURE,
                "resource_type": ResourceType.KEYVAULT,
                "severity": SeverityLevel.HIGH,
                "category": "access_control",
                "description": "Key Vault has no firewall rules configured",
                "remediation": "Configure Key Vault firewall to allow only specific networks.",
                "compliance": ["CIS", "SOC2", "PCI-DSS"]
            },
            # GCP Rules
            "GCP-GCS-001": {
                "provider": CloudProvider.GCP,
                "resource_type": ResourceType.GCS,
                "severity": SeverityLevel.CRITICAL,
                "category": "data_exposure",
                "description": "GCS bucket has allUsers or allAuthenticatedUsers access",
                "remediation": "Remove allUsers and allAuthenticatedUsers bindings from bucket IAM.",
                "compliance": ["CIS", "SOC2", "GDPR"]
            },
            "GCP-COMPUTE-001": {
                "provider": CloudProvider.GCP,
                "resource_type": ResourceType.COMPUTE,
                "severity": SeverityLevel.HIGH,
                "category": "network_security",
                "description": "Firewall rule allows ingress from 0.0.0.0/0",
                "remediation": "Restrict firewall rule source ranges to specific CIDR blocks.",
                "compliance": ["CIS", "PCI-DSS"]
            },
            "GCP-IAM-001": {
                "provider": CloudProvider.GCP,
                "resource_type": ResourceType.IAM_GCP,
                "severity": SeverityLevel.CRITICAL,
                "category": "access_control",
                "description": "Service account has Owner or Editor role at project level",
                "remediation": "Replace broad roles with specific predefined or custom roles.",
                "compliance": ["CIS", "SOC2", "PCI-DSS"]
            }
        }

    def _initialize_compliance(self):
        """Initialize compliance framework mappings."""
        self.compliance_frameworks = {
            "CIS": {
                "name": "CIS Benchmarks",
                "aws_version": "1.5.0",
                "azure_version": "1.4.0",
                "gcp_version": "1.3.0",
                "total_controls": 250
            },
            "SOC2": {
                "name": "SOC 2 Type II",
                "controls": ["CC6.1", "CC6.2", "CC6.3", "CC7.1", "CC7.2"],
                "total_controls": 67
            },
            "PCI-DSS": {
                "name": "PCI DSS v4.0",
                "requirements": ["1", "2", "3", "4", "6", "7", "8", "10", "11"],
                "total_controls": 282
            },
            "HIPAA": {
                "name": "HIPAA Security Rule",
                "controls": ["164.308", "164.310", "164.312"],
                "total_controls": 75
            },
            "GDPR": {
                "name": "GDPR",
                "articles": ["5", "25", "32", "33", "35"],
                "total_controls": 99
            }
        }

    async def authenticate(
        self,
        provider: CloudProvider,
        credentials: Dict[str, str]
    ) -> bool:
        """Authenticate with a cloud provider."""
        if provider in self.providers:
            self.providers[provider]["authenticated"] = True
            return True
        return False

    async def scan_provider(
        self,
        provider: CloudProvider,
        regions: Optional[List[str]] = None
    ) -> SecurityScanResult:
        """Scan a cloud provider for misconfigurations."""
        start_time = time.time()
        scan_id = hashlib.sha256(
            f"scan_{provider.value}_{time.time()}".encode()
        ).hexdigest()[:12]

        # Enumerate resources
        resources = await self._enumerate_resources(provider, regions)

        # Check each resource against rules
        misconfigurations: List[Misconfiguration] = []
        provider_rules = {
            k: v for k, v in self.misconfiguration_rules.items()
            if v["provider"] == provider
        }

        for resource in resources:
            for rule_id, rule in provider_rules.items():
                if resource.resource_type == rule["resource_type"]:
                    is_misconfigured = await self._check_rule(
                        resource, rule_id, rule
                    )
                    if is_misconfigured:
                        misc = Misconfiguration(
                            resource_id=resource.resource_id,
                            resource_type=resource.resource_type.value,
                            provider=provider.value,
                            rule_id=rule_id,
                            severity=rule["severity"],
                            category=rule["category"],
                            description=rule["description"],
                            remediation=rule["remediation"],
                            compliance_impact=rule["compliance"]
                        )
                        misconfigurations.append(misc)
                        resource.misconfigurations.append({
                            "rule_id": rule_id,
                            "severity": rule["severity"].value
                        })

        critical = sum(
            1 for m in misconfigurations
            if m.severity == SeverityLevel.CRITICAL
        )
        high = sum(
            1 for m in misconfigurations
            if m.severity == SeverityLevel.HIGH
        )
        medium = sum(
            1 for m in misconfigurations
            if m.severity == SeverityLevel.MEDIUM
        )
        low = sum(
            1 for m in misconfigurations
            if m.severity == SeverityLevel.LOW
        )

        compliance_score = 1.0 - (
            (critical * 10 + high * 5 + medium * 2 + low * 0.5)
            / max(len(resources) * 10, 1)
        )
        compliance_score = max(0.0, min(1.0, compliance_score))

        self.all_resources.extend(resources)

        result = SecurityScanResult(
            scan_id=scan_id,
            provider=provider,
            total_resources=len(resources),
            misconfigured_resources=len(set(
                m.resource_id for m in misconfigurations
            )),
            critical_findings=critical,
            high_findings=high,
            medium_findings=medium,
            low_findings=low,
            compliance_score=compliance_score,
            misconfigurations=misconfigurations,
            scan_duration=time.time() - start_time
        )

        self.providers[provider]["scan_history"].append(result)
        return result

    async def _enumerate_resources(
        self,
        provider: CloudProvider,
        regions: Optional[List[str]] = None
    ) -> List[CloudResource]:
        """Enumerate cloud resources for the given provider."""
        resources = []
        default_regions = {
            CloudProvider.AWS: ["us-east-1", "us-west-2", "eu-west-1"],
            CloudProvider.AZURE: ["eastus", "westeurope"],
            CloudProvider.GCP: ["us-central1", "europe-west1"]
        }

        scan_regions = regions or default_regions.get(provider, ["us-east-1"])

        resource_types = {
            CloudProvider.AWS: [
                ResourceType.S3, ResourceType.EC2, ResourceType.IAM,
                ResourceType.RDS, ResourceType.LAMBDA
            ],
            CloudProvider.AZURE: [
                ResourceType.BLOB, ResourceType.VM,
                ResourceType.KEYVAULT, ResourceType.SQL
            ],
            CloudProvider.GCP: [
                ResourceType.GCS, ResourceType.COMPUTE,
                ResourceType.IAM_GCP, ResourceType.CLOUDSQL
            ]
        }

        for region in scan_regions:
            for r_type in resource_types.get(provider, []):
                for i in range(3):  # Simulate 3 resources per type per region
                    resource = CloudResource(
                        resource_id=f"{provider.value}-{r_type.value}-{region}-{i}",
                        resource_type=r_type,
                        provider=provider,
                        region=region,
                        name=f"{r_type.value}-{i}-{region}",
                        configuration={"simulated": True}
                    )
                    resources.append(resource)

        return resources

    async def _check_rule(
        self,
        resource: CloudResource,
        rule_id: str,
        rule: Dict
    ) -> bool:
        """Check a resource against a specific misconfiguration rule."""
        # Simulate rule evaluation - some resources will be flagged
        return hash(f"{resource.resource_id}_{rule_id}") % 3 == 0

    async def multi_cloud_scan(
        self,
        providers: Optional[List[CloudProvider]] = None
    ) -> Dict[str, SecurityScanResult]:
        """Scan multiple cloud providers simultaneously."""
        target_providers = providers or [
            CloudProvider.AWS, CloudProvider.AZURE, CloudProvider.GCP
        ]

        results = {}
        tasks = [
            self.scan_provider(provider)
            for provider in target_providers
        ]
        scan_results = await asyncio.gather(*tasks, return_exceptions=True)

        for provider, result in zip(target_providers, scan_results):
            if isinstance(result, Exception):
                results[provider.value] = {"error": str(result)}
            else:
                results[provider.value] = result

        return results

    async def generate_compliance_report(
        self,
        framework: str
    ) -> Dict:
        """Generate compliance report for a specific framework."""
        framework_config = self.compliance_frameworks.get(framework, {})

        applicable_findings = []
        for resource in self.all_resources:
            for misc in resource.misconfigurations:
                rule = self.misconfiguration_rules.get(misc["rule_id"], {})
                if framework in rule.get("compliance", []):
                    applicable_findings.append({
                        "resource": resource.resource_id,
                        "rule": misc["rule_id"],
                        "severity": misc["severity"],
                        "description": rule.get("description", "")
                    })

        return {
            "framework": framework,
            "framework_config": framework_config,
            "total_findings": len(applicable_findings),
            "findings": applicable_findings,
            "compliance_status": "non_compliant" if applicable_findings
                                 else "compliant"
        }
```

---

## ContainerSecurity Class

```python
class ContainerRuntime(Enum):
    DOCKER = "docker"
    CONTAINERD = "containerd"
    CRIO = "cri-o"
    PODMAN = "podman"


@dataclass
class ContainerImage:
    image_id: str
    name: str
    tag: str
    registry: str
    digest: str
    size_mb: float
    created_at: float
    vulnerabilities: List[Dict] = field(default_factory=list)
    misconfigurations: List[Dict] = field(default_factory=list)
    base_image: str = ""
    packages: List[str] = field(default_factory=list)


@dataclass
class KubernetesResource:
    resource_type: str
    name: str
    namespace: str
    cluster: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    security_issues: List[Dict] = field(default_factory=list)


@dataclass
class ContainerScanResult:
    scan_id: str
    images_scanned: int
    containers_scanned: int
    total_vulnerabilities: int
    critical_vulns: int
    high_vulns: int
    misconfigurations: int
    k8s_issues: int
    risk_score: float
    timestamp: float = field(default_factory=time.time)


class ContainerSecurity:
    """Container and Kubernetes security analysis engine."""

    def __init__(self):
        self.scanned_images: Dict[str, ContainerImage] = {}
        self.k8s_resources: List[KubernetesResource] = []
        self.vulnerability_db: Dict[str, Dict] = {}
        self.k8s_security_rules: List[Dict] = []
        self._initialize_k8s_rules()

    def _initialize_k8s_rules(self):
        """Initialize Kubernetes security validation rules."""
        self.k8s_security_rules = [
            {
                "id": "K8S-001",
                "check": "run_as_non_root",
                "description": "Container should not run as root",
                "severity": SeverityLevel.HIGH,
                "remediation": "Set runAsNonRoot: true in securityContext"
            },
            {
                "id": "K8S-002",
                "check": "privileged_container",
                "description": "Container should not be privileged",
                "severity": SeverityLevel.CRITICAL,
                "remediation": "Set privileged: false in securityContext"
            },
            {
                "id": "K8S-003",
                "check": "read_only_filesystem",
                "description": "Container filesystem should be read-only",
                "severity": SeverityLevel.MEDIUM,
                "remediation": "Set readOnlyRootFilesystem: true"
            },
            {
                "id": "K8S-004",
                "check": "resource_limits",
                "description": "Resource limits should be defined",
                "severity": SeverityLevel.HIGH,
                "remediation": "Define requests and limits for CPU and memory"
            },
            {
                "id": "K8S-005",
                "check": "network_policy",
                "description": "Network policy should be defined for namespace",
                "severity": SeverityLevel.MEDIUM,
                "remediation": "Create NetworkPolicy to restrict pod communication"
            },
            {
                "id": "K8S-006",
                "check": "host_namespace",
                "description": "Container should not share host PID/IPC namespaces",
                "severity": SeverityLevel.HIGH,
                "remediation": "Set hostPID: false and hostIPC: false"
            },
            {
                "id": "K8S-007",
                "check": "capability_drop",
                "description": "All capabilities should be dropped by default",
                "severity": SeverityLevel.HIGH,
                "remediation": "Set capabilities.drop: [ALL] in securityContext"
            }
        ]

    async def scan_container_image(
        self,
        image_name: str,
        tag: str = "latest"
    ) -> ContainerImage:
        """Scan a container image for vulnerabilities and misconfigurations."""
        image_id = hashlib.sha256(
            f"{image_name}:{tag}".encode()
        ).hexdigest()[:16]

        # Simulate vulnerability scan
        vulnerabilities = []
        severities = ["critical", "high", "medium", "low"]
        for i in range(random.randint(2, 15)):
            cve_id = f"CVE-2024-{random.randint(10000, 99999)}"
            vulnerabilities.append({
                "cve": cve_id,
                "severity": random.choice(severities),
                "package": f"package_{i}",
                "version": f"1.{i}.0",
                "fixed_version": f"1.{i}.1",
                "description": f"Vulnerability in package_{i}"
            })

        # Check for misconfigurations
        misconfigurations = []
        image_checks = [
            "running_as_root",
            "sudo_installed",
            "ssh_server_present",
            "secrets_in_env",
            "unpinned_base_image",
            "no_healthcheck",
            "exposed_privileged_ports"
        ]
        for check in image_checks:
            if random.random() < 0.3:
                misconfigurations.append({
                    "check": check,
                    "severity": "high" if check in [
                        "running_as_root", "secrets_in_env"
                    ] else "medium",
                    "description": f"Image {image_name} has {check} issue"
                })

        image = ContainerImage(
            image_id=image_id,
            name=image_name,
            tag=tag,
            registry="docker.io",
            digest=f"sha256:{image_id}",
            size_mb=round(random.uniform(50, 500), 1),
            created_at=time.time(),
            vulnerabilities=vulnerabilities,
            misconfigurations=misconfigurations,
            base_image="ubuntu:22.04"
        )

        self.scanned_images[image_id] = image
        return image

    async def scan_kubernetes_cluster(
        self,
        cluster_name: str
    ) -> List[KubernetesResource]:
        """Scan Kubernetes cluster for security issues."""
        namespaces = ["default", "kube-system", "production", "staging"]
        resource_types = ["Deployment", "Pod", "Service", "ConfigMap"]

        resources = []
        for ns in namespaces:
            for rtype in resource_types:
                for i in range(2):
                    k8s_resource = KubernetesResource(
                        resource_type=rtype,
                        name=f"{rtype.lower()}-{i}",
                        namespace=ns,
                        cluster=cluster_name
                    )

                    # Apply security rules
                    for rule in self.k8s_security_rules:
                        if random.random() < 0.25:
                            k8s_resource.security_issues.append({
                                "rule_id": rule["id"],
                                "check": rule["check"],
                                "severity": rule["severity"].value,
                                "description": rule["description"],
                                "remediation": rule["remediation"]
                            })

                    resources.append(k8s_resource)

        self.k8s_resources.extend(resources)
        return resources

    async def full_container_scan(
        self,
        images: List[str],
        clusters: List[str]
    ) -> ContainerScanResult:
        """Perform full container security scan."""
        scan_id = hashlib.sha256(
            f"container_scan_{time.time()}".encode()
        ).hexdigest()[:12]

        # Scan images
        image_tasks = [
            self.scan_container_image(img) for img in images
        ]
        scanned = await asyncio.gather(*image_tasks, return_exceptions=True)

        # Scan clusters
        cluster_tasks = [
            self.scan_kubernetes_cluster(c) for c in clusters
        ]
        cluster_results = await asyncio.gather(*cluster_tasks)

        # Aggregate results
        total_vulns = sum(
            len(img.vulnerabilities)
            for img in self.scanned_images.values()
        )
        critical = sum(
            1 for img in self.scanned_images.values()
            for v in img.vulnerabilities
            if v["severity"] == "critical"
        )
        high = sum(
            1 for img in self.scanned_images.values()
            for v in img.vulnerabilities
            if v["severity"] == "high"
        )
        misc_count = sum(
            len(img.misconfigurations)
            for img in self.scanned_images.values()
        )
        k8s_issues = sum(
            len(r.security_issues) for r in self.k8s_resources
        )

        risk_score = min(1.0, (
            critical * 0.3 + high * 0.15 + misc_count * 0.05
            + k8s_issues * 0.05
        ))

        return ContainerScanResult(
            scan_id=scan_id,
            images_scanned=len(images),
            containers_scanned=sum(
                len(r) for r in cluster_results
            ),
            total_vulnerabilities=total_vulns,
            critical_vulns=critical,
            high_vulns=high,
            misconfigurations=misc_count,
            k8s_issues=k8s_issues,
            risk_score=round(risk_score, 2)
        )

    async def generate_hardening_manifest(
        self,
        image_name: str
    ) -> Dict:
        """Generate Kubernetes hardening manifest for an image."""
        return {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": f"{image_name.split('/')[-1]}-hardened",
                "labels": {"security": "hardened"}
            },
            "spec": {
                "securityContext": {
                    "runAsNonRoot": True,
                    "runAsUser": 1000,
                    "fsGroup": 2000,
                    "seccompProfile": {"type": "RuntimeDefault"}
                },
                "containers": [{
                    "name": image_name.split('/')[-1],
                    "image": image_name,
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "readOnlyRootFilesystem": True,
                        "capabilities": {"drop": ["ALL"]}
                    },
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "128Mi"},
                        "limits": {"cpu": "500m", "memory": "512Mi"}
                    }
                }]
            }
        }
```

---

## Usage Example

```python
async def main():
    orchestrator = CloudSecurityOrchestrator()

    # Authenticate
    await orchestrator.authenticate(
        CloudProvider.AWS, {"access_key": "AKIA...", "secret": "..."}
    )
    await orchestrator.authenticate(
        CloudProvider.AZURE, {"tenant_id": "...", "subscription_id": "..."}
    )

    # Multi-cloud scan
    results = await orchestrator.multi_cloud_scan()
    for provider, result in results.items():
        if isinstance(result, SecurityScanResult):
            print(f"{provider}: {result.critical_findings} critical, "
                  f"score: {result.compliance_score:.2f}")

    # Compliance report
    cis_report = await orchestrator.generate_compliance_report("CIS")

    # Container security
    container_sec = ContainerSecurity()
    scan = await container_sec.full_container_scan(
        images=["nginx:latest", "python:3.11", "alpine:3.18"],
        clusters=["prod-cluster", "staging-cluster"]
    )
    print(f"Container scan: {scan.critical_vulns} critical vulns")

    # Hardening manifest
    manifest = await container_sec.generate_hardening_manifest("myapp:latest")

asyncio.run(main())
```
