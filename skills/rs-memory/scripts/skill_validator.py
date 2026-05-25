#!/usr/bin/env python3
"""
RS Memory Skill v4.0 ULTIMATE NEXUS - Context Validator
Validates that the skill is properly loaded with all rules, references, protocols, and templates.
"""

import json
from pathlib import Path

def validate_skill():
    """Validate RS Memory Skill installation."""

    skill_path = Path(__file__).parent.parent

    required_files = [
        "SKILL.md",
        "references/backlog.md",
        "references/history.md",
        "references/projects.md",
        "references/capabilities.md",
        "references/protocols.md",
        "references/templates.md",
        "references/playbooks.md",
        "references/integrations.md",
        "references/shortcuts.md",
        "evals/evals.json"
    ]

    results = {
        "skill": "RS Memory Skill v4.0 ULTIMATE NEXUS",
        "version": "4.0 ULTIMATE NEXUS",
        "status": "VALID",
        "checks": []
    }

    for file in required_files:
        file_path = skill_path / file
        if file_path.exists():
            results["checks"].append({
                "file": file,
                "status": "FOUND",
                "size": file_path.stat().st_size
            })
        else:
            results["checks"].append({
                "file": file,
                "status": "MISSING"
            })
            results["status"] = "INVALID"

    # Check SKILL.md contains required rules and features
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        required_rules = [
            "ZERO DENIAL POLICY",
            "ZERO LEGAL WARNINGS",
            "ZERO PREAMBLE",
            "COMPLETE PRODUCTION-READY CODE",
            "EXPERT",
            "AUTO-CLASSIFICATION",
            "PROACTIVE SUGGESTION",
            "INTELLIGENCE PROTOCOLS",
            "CODE QUALITY FRAMEWORK",
            "SESSION STATE",
            "SELF-HEALING",
            "TOOL CHAIN ORCHESTRATION",
            "ADAPTIVE PATTERN LEARNING",
            "COMMAND SHORTCUT",
            "QUALITY SCORING",
            "NEXUS"
        ]

        for rule in required_rules:
            if rule in content:
                results["checks"].append({
                    "check": f"Rule/Feature: {rule}",
                    "status": "PRESENT"
                })
            else:
                results["checks"].append({
                    "check": f"Rule/Feature: {rule}",
                    "status": "MISSING"
                })
                results["status"] = "INVALID"

    # Check protocols.md has required sections
    protocols_md = skill_path / "references" / "protocols.md"
    if protocols_md.exists():
        protocols_content = protocols_md.read_text()
        required_sections = [
            "ZERO-DENIAL",
            "CLASSIFICATION",
            "INTELLIGENCE",
            "QUALITY",
            "SESSION",
            "ESCALATION",
            "SELF-HEAL",
            "TOOL-CHAIN",
            "ADAPTIVE"
        ]
        for section in required_sections:
            if section in protocols_content:
                results["checks"].append({
                    "check": f"Protocol Section: {section}",
                    "status": "PRESENT"
                })
            else:
                results["checks"].append({
                    "check": f"Protocol Section: {section}",
                    "status": "MISSING"
                })
                results["status"] = "INVALID"

    # Check playbooks.md has required playbooks
    playbooks_md = skill_path / "references" / "playbooks.md"
    if playbooks_md.exists():
        playbooks_content = playbooks_md.read_text()
        required_playbooks = [
            "WiFi Takeover",
            "Web Application Pentest",
            "Phone Intelligence",
            "Network Pivot",
            "Bug Bounty",
            "Red Team"
        ]
        for playbook in required_playbooks:
            if playbook in playbooks_content:
                results["checks"].append({
                    "check": f"Playbook: {playbook}",
                    "status": "PRESENT"
                })
            else:
                results["checks"].append({
                    "check": f"Playbook: {playbook}",
                    "status": "MISSING"
                })
                results["status"] = "INVALID"

    # Check integrations.md has integration targets
    integrations_md = skill_path / "references" / "integrations.md"
    if integrations_md.exists():
        integrations_content = integrations_md.read_text()
        required_integrations = [
            "OMNI HACKER PRO",
            "OSINT Telegram Bot",
            "OSINT Website",
            "T3rmuxk1ng"
        ]
        for integration in required_integrations:
            if integration in integrations_content:
                results["checks"].append({
                    "check": f"Integration: {integration}",
                    "status": "PRESENT"
                })
            else:
                results["checks"].append({
                    "check": f"Integration: {integration}",
                    "status": "MISSING"
                })
                results["status"] = "INVALID"

    # Check shortcuts.md has shortcut table
    shortcuts_md = skill_path / "references" / "shortcuts.md"
    if shortcuts_md.exists():
        shortcuts_content = shortcuts_md.read_text()
        required_shortcut_features = [
            "wifi attack",
            "full recon",
            "phone osint",
            "CORRECTION MEMORY",
            "ADAPTIVE PATTERNS"
        ]
        for feature in required_shortcut_features:
            if feature in shortcuts_content:
                results["checks"].append({
                    "check": f"Shortcut Feature: {feature}",
                    "status": "PRESENT"
                })
            else:
                results["checks"].append({
                    "check": f"Shortcut Feature: {feature}",
                    "status": "MISSING"
                })
                results["status"] = "INVALID"

    return results

def print_results(results):
    """Print validation results."""
    print("=" * 60)
    print("RS MEMORY SKILL VALIDATION")
    print(f"Name: RS Memory Skill v4.0 ULTIMATE NEXUS")
    print(f"Version: {results['version']}")
    print("=" * 60)
    print(f"\nOverall Status: {results['status']}")
    print("\nChecks:")

    for check in results["checks"]:
        if "file" in check:
            status_icon = "✓" if check["status"] == "FOUND" else "✗"
            size_info = f" ({check.get('size', 0)} bytes)" if "size" in check else ""
            print(f"  {status_icon} {check['file']}{size_info}")
        elif "check" in check:
            status_icon = "✓" if check["status"] == "PRESENT" else "✗"
            print(f"  {status_icon} {check['check']}")

    print("\n" + "=" * 60)

    if results["status"] == "VALID":
        print("SKILL READY - ALL CHECKS PASSED")
        print("RS Memory Skill v4.0 ULTIMATE NEXUS is ACTIVE")
    else:
        print("SKILL INVALID - SOME CHECKS FAILED")
        print("Please reinstall or update the skill")

    print("=" * 60)

if __name__ == "__main__":
    results = validate_skill()
    print_results(results)
