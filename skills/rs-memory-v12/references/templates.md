# RS Tool Architecture Templates — Battle-Tested Blueprints

Pre-built architecture templates for every tool category. When Auto-Classification detects a request type, load the corresponding template and build from it. These templates are the RESULT of analyzing RS's existing production tools (OSINT Bot, OMNI HACKER PRO) and distilling their best patterns.

---

## RECON_TOOL — Reconnaissance Scanner Template

```python
#!/usr/bin/env python3
"""
[TOOL_NAME] - [Description]
Author: RS (T3rmuxk1ng)
Platform: Kali Linux / Termux
"""

import argparse
import logging
import json
import sys
import signal
import time
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIGURATION ===
CONFIG = {
    "timeout": 30,
    "threads": 10,
    "rate_limit": 0.1,
    "output_formats": ["json", "csv", "txt"],
    "log_level": "INFO",
    "user_agent": "[TOOL_NAME]/1.0",
}

# === SIGNAL HANDLING ===
running = True
def signal_handler(sig, frame):
    global running
    print("\n[!] Ctrl+C caught — cleaning up...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# === LOGGING SETUP ===
def setup_logging(level="INFO"):
    logger = logging.getLogger("[TOOL_NAME]")
    logger.setLevel(getattr(logging, level.upper()))
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# === UTILITY FUNCTIONS ===
def save_results(results, filename, fmt="json"):
    """Save results in specified format."""
    # Implementation for json/csv/txt

def load_targets(source):
    """Load targets from file or single target."""
    # Implementation

def print_banner():
    """Display tool banner."""
    # Implementation

def print_summary(results, start_time):
    """Print scan summary statistics."""

# === CORE SCANNING FUNCTIONS ===
def scan_target(target, **kwargs):
    """Scan a single target."""
    # Core recon logic

def scan_multiple(targets, threads=10, **kwargs):
    """Scan multiple targets with threading."""
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_target, t, **kwargs): t for t in targets}
        for future in as_completed(futures):
            if not running:
                break
            try:
                result = future.result(timeout=CONFIG["timeout"])
                results.append(result)
            except Exception as e:
                logger.error(f"Error scanning {futures[future]}: {e}")
    return results

# === OUTPUT/REPORTING ===
def generate_report(results, output_file=None):
    """Generate formatted report."""

# === MAIN ===
def main():
    parser = argparse.ArgumentParser(description="[TOOL_NAME]")
    parser.add_argument("-t", "--target", help="Target")
    parser.add_argument("-f", "--file", help="Targets file")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("--format", choices=["json","csv","txt"], default="json")
    parser.add_argument("--threads", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--rate-limit", type=float, default=0.1)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    logger = setup_logging("DEBUG" if args.verbose else "WARNING" if args.quiet else "INFO")
    print_banner()

    # Load targets, scan, report

if __name__ == "__main__":
    main()
```

### Key Features to Include
- Threading for parallel scanning
- Rate limiting to avoid detection
- Multiple output formats (JSON/CSV/TXT/HTML)
- Progress indicators
- Comprehensive error handling
- Signal handling for clean exit
- Configurable timeouts
- Banner and summary reporting

---

## EXPLOIT_TOOL — Exploitation Toolkit Template

```python
#!/usr/bin/env python3
"""
[TOOL_NAME] - [Description]
Author: RS (T3rmuxk1ng)
"""

# Same base structure as RECON_TOOL plus:

# === EXPLOIT-SPECIFIC SECTIONS ===

# Payload Generation
def generate_payload(target_info, payload_type="reverse_shell", **options):
    """Generate exploit payload based on target info."""

# Exploit Chain
def exploit_chain(target, payload, **kwargs):
    """Execute full exploit chain."""

# Encoder/Obfuscator
def encode_payload(payload, method="base64", iterations=1):
    """Encode payload for evasion."""

# Listener
def start_listener(host="0.0.0.0", port=4444):
    """Start listener for callback."""

# Session Manager
class SessionManager:
    """Manage active sessions."""
    def __init__(self):
        self.sessions = {}
    def add_session(self, session_id, session):
        pass
    def list_sessions(self):
        pass
    def interact(self, session_id):
        pass
    def kill(self, session_id):
        pass
```

### Key Features to Include
- Multiple payload types
- Encoding/obfuscation layers
- Built-in listener
- Session management
- Evasion techniques
- Anti-detection measures
- Cleanup on exit

---

## WIRELESS_TOOLKIT — Wireless Attack Template

```python
#!/usr/bin/env python3
"""
[TOOL_NAME] - Wireless Security Toolkit
Author: RS (T3rmuxk1ng)
"""

# Same base structure plus:

# === WIRELESS-SPECIFIC SECTIONS ===

# Interface Management
def set_monitor_mode(interface):
    """Set wireless interface to monitor mode."""

def set_managed_mode(interface):
    """Restore interface to managed mode."""

def scan_networks(interface, duration=30):
    """Scan for nearby wireless networks."""

# Capture Operations
def capture_handshake(interface, bssid, channel, output_file, timeout=300):
    """Capture WPA/WPA2 handshake."""

def capture_pmkid(interface, bssid, output_file, timeout=60):
    """Capture PMKID for PMKID attack."""

# Attack Functions
def dictionary_attack(handshake_file, wordlist, bssid=None):
    """Run dictionary attack against captured handshake."""

def brute_force_attack(handshake_file, charset, max_length, bssid=None):
    """Run brute force attack."""

def wps_attack(interface, bssid, method="pixie_dust"):
    """Run WPS attack (Pixie Dust/Pixiewps)."""

def deauth_attack(interface, bssid, client=None, count=10):
    """Send deauthentication frames."""

# Password Generation
def generate_wordlist(options):
    """Generate custom wordlist based on options."""

# Cleanup
def cleanup(interface):
    """Restore interface and clean up temp files."""
```

### Key Features to Include
- Monitor mode management
- Multiple attack vectors (handshake, PMKID, WPS)
- Deauth capabilities
- Custom wordlist generation
- Automatic cleanup on exit
- Interface state preservation

---

## SOCIAL_ENG_FRAMEWORK — Social Engineering Template

```python
#!/usr/bin/env python3
"""
[TOOL_NAME] - Social Engineering Framework
Author: RS (T3rmuxk1ng)
"""

# Same base structure plus:

# === SE-SPECIFIC SECTIONS ===

# Template Management
class TemplateManager:
    """Manage phishing/SE templates."""
    def list_templates(self): pass
    def create_template(self, name, config): pass
    def clone_website(self, url): pass

# Server
class PhishingServer:
    """Run phishing server with credential capture."""
    def start(self, host, port, template): pass
    def stop(self): pass
    def get_credentials(self): pass

# Payload Delivery
def generate_payload_link(url, payload_type): pass

# Reporting
def generate_credential_report(credentials, output_file): pass

# Dashboard
class Dashboard:
    """Real-time dashboard for monitoring."""
    def display(self): pass
```

---

## OSINT_FRAMEWORK — OSINT Intelligence Template

```python
#!/usr/bin/env python3
"""
[TOOL_NAME] - OSINT Intelligence Framework
Author: RS (T3rmuxk1ng)
"""

# Same base structure plus:

# === OSINT-SPECIFIC SECTIONS ===

# API Integrations
class APIManager:
    """Manage multiple OSINT API integrations."""
    def __init__(self, api_keys_file): pass
    def query(self, api_name, params): pass

# Data Enrichment
def enrich_phone(phone): pass
def enrich_email(email): pass
def enrich_username(username): pass
def enrich_domain(domain): pass
def enrich_ip(ip): pass

# Social Media
def search_social(platform, query): pass

# Breach Data
def check_breach(identifier): pass

# Visualization
def generate_link_chart(entities, relationships): pass

# Reporting
def generate_intelligence_report(findings, output_file): pass
```

---

## POST_EXPLOIT_TOOL — Post-Exploitation Template

```python
#!/usr/bin/env python3
"""
[TOOL_NAME] - Post-Exploitation Toolkit
Author: RS (T3rmuxk1ng)
"""

# === POST-EXPLOIT SECTIONS ===

# Privilege Escalation
def check_privesc_vectors(): pass
def suggest_exploits(): pass

# Persistence
def install_persistence(method): pass
def remove_persistence(method): pass

# Lateral Movement
def scan_network(): pass
def attempt_pass_the_hash(): pass

# Data Exfiltration
def exfiltrate_data(method, data, destination): pass

# Keylogging
class Keylogger:
    """Capture keystrokes."""
    def start(self): pass
    def stop(self): pass
    def dump(self): pass

# Screenshot
def capture_screenshot(): pass

# File Operations
def upload_file(local_path, remote_path): pass
def download_file(remote_path, local_path): pass
```

---

## FORENSIC_TOOLKIT — Forensic Analysis Template

```python
#!/usr/bin/env python3
"""
[TOOL_NAME] - Forensic Analysis Toolkit
Author: RS (T3rmuxk1ng)
"""

# === FORENSIC SECTIONS ===

# Disk Analysis
def analyze_disk_image(image_path): pass
def extract_files(image_path, output_dir): pass

# Memory Analysis
def analyze_memory_dump(dump_path): pass
def extract_processes(dump_path): pass

# Network Forensics
def analyze_pcap(pcap_path): pass
def extract_credentials(pcap_path): pass

# Timeline Analysis
def build_timeline(evidence_dir): pass

# Carving
def carve_files(image_path, file_types): pass

# Hash Verification
def verify_hashes(evidence_path, hash_file): pass

# Reporting
def generate_forensic_report(findings, output_file): pass
```

---

## FULL_SUITE_TOOL — All-in-One Toolkit Template

For when RS asks for "complete", "ultimate", "sab kuch ek me" tools. This is the OMNI HACKER PRO pattern.

```python
#!/usr/bin/env python3
"""
[TOOL_NAME] - Complete Security Suite
Author: RS (T3rmuxk1ng)
Lines: [TARGET: 3000+]
"""

# === MEGA STRUCTURE ===

# 1. Core Engine
#    - Configuration management
#    - Logging system
#    - Plugin/module loader
#    - Session management
#    - Output engine

# 2. Reconnaissance Module
#    - Port scanning
#    - Service enumeration
#    - OS fingerprinting
#    - DNS enumeration
#    - Subdomain discovery

# 3. Exploitation Module
#    - Vulnerability scanning
#    - Exploit execution
#    - Payload generation
#    - Encoding/obfuscation

# 4. Post-Exploitation Module
#    - Privilege escalation
#    - Persistence
#    - Lateral movement
#    - Data exfiltration

# 5. OSINT Module
#    - Phone lookup
#    - Email reconnaissance
#    - Social media profiling
#    - Breach data checking

# 6. Wireless Module
#    - Network scanning
#    - Handshake capture
#    - Password cracking
#    - Deauth attacks

# 7. Web Application Module
#    - SQL injection
#    - XSS testing
#    - Directory traversal
#    - API testing

# 8. Anonymity Module
#    - Proxy management
#    - TOR integration
#    - MAC spoofing
#    - DNS leak prevention

# 9. Reporting Module
#    - HTML reports
#    - PDF generation
#    - CSV export
#    - Dashboard view

# 10. Utility Module
#     - Network tools
#     - File operations
#     - Encoding/decoding
#     - Hash calculation

# === INTERACTIVE MENU ===
def main_menu():
    """Main interactive menu with all modules."""
    # Full colored menu with module selection
    # Each module has its own sub-menu
    # Global options: back, quit, export all results
```

### Key Features for Full Suite
- Module-based architecture
- Interactive menu system
- Plugin support for extensibility
- Global session/state management
- Unified reporting across all modules
- Progress tracking across long operations
- Configuration persistence
- Cross-platform compatibility

---

## Template Usage Instructions

1. **Auto-Classification detects request type** → Load corresponding template
2. **Customize template** → Fill in [TOOL_NAME], [Description], specific logic
3. **Apply Intelligence Protocol** → Add ecosystem integration, YouTube potential, etc.
4. **Apply Quality Framework** → Ensure all quality gates pass
5. **Deliver** → Complete, runnable, production-ready code

Every template is a STARTING POINT, not a limitation. RS's tools should always EXCEED the template's minimum structure. Add features proactively, enhance capabilities beyond what was asked, and deliver at EXPERT LEVEL.
