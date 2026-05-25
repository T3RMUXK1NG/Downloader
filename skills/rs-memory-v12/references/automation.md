# RS Automation Scripts — One-Command Deployment

Every tool RS builds must be deployable with ONE command. This reference provides automation patterns for zero-friction deployment.

---

## DEPLOYMENT PATTERNS

### Pattern 1: Single-File Tool

```python
#!/usr/bin/env python3
"""
[TOOL_NAME] - [Description]
Author: RS (T3rmuxk1ng)

ONE-COMMAND DEPLOYMENT:
    pip install [requirements]
    python3 [tool_name].py --help
"""

# === AUTO-DEPENDENCY CHECK ===
def check_dependencies():
    """Auto-check and guide dependency installation."""
    required = {
        'requests': 'pip install requests',
        'rich': 'pip install rich',
        'beautifulsoup4': 'pip install beautifulsoup4',
    }
    missing = []
    for package, install_cmd in required.items():
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(install_cmd)
    
    if missing:
        print("[!] Missing dependencies. Run:")
        for cmd in missing:
            print(f"    {cmd}")
        print("\nThen run this tool again.")
        return False
    return True

# === AUTO-CONFIGURATION ===
def auto_configure():
    """Auto-configure tool with sensible defaults."""
    config_dir = Path.home() / ".rs-tools" / "config"
    config_file = config_dir / "[tool_name]_config.json"
    
    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        default_config = {
            "timeout": 30,
            "threads": 10,
            "output_dir": str(Path.home() / ".rs-tools" / "output"),
        }
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"[*] Created default config at {config_file}")
    
    return json.loads(config_file.read_text())

# === MAIN ===
if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    
    config = auto_configure()
    main()
```

**Deployment Command:**
```bash
python3 tool_name.py --help
```

---

### Pattern 2: Package Installation

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="[tool-name]",
    version="1.0.0",
    author="RS (T3rmuxk1ng)",
    description="[Description]",
    py_modules=["tool_name"],
    install_requires=[
        "requests>=2.28.0",
        "rich>=13.0.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "tool-name=tool_name:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
```

**Deployment Commands:**
```bash
# From PyPI (after publishing)
pip install tool-name
tool-name --help

# From local
pip install .
tool-name --help

# From GitHub
pip install git+https://github.com/rs/[tool-name].git
tool-name --help
```

---

### Pattern 3: Git Clone + Run

```bash
#!/bin/bash
# install.sh - One-command installer

echo "[*] Installing [TOOL_NAME]..."

# Clone repository
git clone https://github.com/rs/[tool-name].git
cd [tool-name]

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python3 main.py --help

echo "[+] Installation complete!"
echo "[*] Run with: python3 main.py [options]"
```

**Deployment Command:**
```bash
curl -sSL https://raw.githubusercontent.com/rs/[tool-name]/main/install.sh | bash
```

---

### Pattern 4: Termux One-Liner

```bash
# Termux-optimized one-liner deployment
pkg update && pkg install python git -y && pip install requests rich && git clone https://github.com/rs/[tool-name] && cd [tool-name] && python3 main.py --help
```

**Breakdown:**
1. `pkg update` - Update package lists
2. `pkg install python git -y` - Install Python and Git
3. `pip install requests rich` - Install dependencies
4. `git clone ...` - Clone tool
5. `cd [tool-name]` - Navigate to directory
6. `python3 main.py --help` - Run tool

---

## SHARED INFRASTRUCTURE

### RS Tools Directory Structure

```
~/.rs-tools/
├── config/           # Shared configuration
│   ├── global.json   # Global settings
│   ├── osint.json    # OSINT tool config
│   └── omni.json     # OMNI HACKER PRO config
├── output/           # Shared output directory
│   ├── [tool-name]/  # Per-tool output
│   └── reports/      # Generated reports
├── cache/            # Shared cache
│   ├── api_cache/    # API response cache
│   └── scan_cache/   # Scan result cache
├── logs/             # Shared logs
│   └── [tool-name].log
└── data/             # Shared data
    ├── wordlists/    # Common wordlists
    └── payloads/     # Common payloads
```

### Initialization Script

```python
#!/usr/bin/env python3
"""Initialize RS Tools shared infrastructure."""

from pathlib import Path
import json

def init_rs_tools():
    """Create shared directory structure."""
    base = Path.home() / ".rs-tools"
    
    directories = [
        "config",
        "output",
        "cache/api_cache",
        "cache/scan_cache",
        "logs",
        "data/wordlists",
        "data/payloads",
    ]
    
    for directory in directories:
        (base / directory).mkdir(parents=True, exist_ok=True)
    
    # Create global config
    global_config = base / "config" / "global.json"
    if not global_config.exists():
        config = {
            "user": "RS",
            "platform": "auto",
            "default_timeout": 30,
            "default_threads": 10,
            "color_output": True,
            "log_level": "INFO",
        }
        global_config.write_text(json.dumps(config, indent=2))
    
    print(f"[+] RS Tools initialized at {base}")
    return base

if __name__ == "__main__":
    init_rs_tools()
```

---

## AUTO-UPDATE SYSTEM

### Self-Updating Tool Pattern

```python
#!/usr/bin/env python3
"""Tool with auto-update capability."""

import requests
from pathlib import Path

VERSION = "1.0.0"
GITHUB_REPO = "rs/tool-name"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/VERSION"

def check_for_updates():
    """Check if a newer version is available."""
    try:
        response = requests.get(VERSION_URL, timeout=5)
        latest = response.text.strip()
        if latest > VERSION:
            print(f"[!] Update available: {VERSION} -> {latest}")
            print(f"[!] Run: pip install --upgrade {GITHUB_REPO}")
            return True
    except:
        pass
    return False

def auto_update():
    """Automatically update if new version available."""
    if check_for_updates():
        import subprocess
        subprocess.run(["pip", "install", "--upgrade", f"git+https://github.com/{GITHUB_REPO}.git"])
        print("[+] Updated! Restart the tool.")
        sys.exit(0)
```

---

## CONFIGURATION MANAGEMENT

### Configuration Hierarchy

```python
def load_config():
    """Load configuration with priority hierarchy."""
    config = {}
    
    # 1. Default values
    defaults = {
        "timeout": 30,
        "threads": 10,
        "output_format": "json",
    }
    config.update(defaults)
    
    # 2. Global config file
    global_config = Path.home() / ".rs-tools" / "config" / "global.json"
    if global_config.exists():
        config.update(json.loads(global_config.read_text()))
    
    # 3. Tool-specific config file
    tool_config = Path.home() / ".rs-tools" / "config" / "[tool]_config.json"
    if tool_config.exists():
        config.update(json.loads(tool_config.read_text()))
    
    # 4. Environment variables
    for key in config:
        env_val = os.environ.get(f"RS_{key.upper()}")
        if env_val:
            config[key] = type(config[key])(env_val)
    
    # 5. CLI arguments (highest priority)
    # Handled by argparse
    
    return config
```

---

## PLATFORM DETECTION

### Automatic Platform Adaptation

```python
import platform
import os
import shutil

class PlatformDetector:
    """Detect and adapt to different platforms."""
    
    def __init__(self):
        self.is_termux = "com.termux" in os.environ.get("PREFIX", "")
        self.is_kali = os.path.exists("/etc/kali-linux-frozen") or "kali" in platform.platform().lower()
        self.is_wsl = "microsoft" in platform.uname().release.lower()
        self.is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        self.has_wifi = self._check_wifi_capability()
    
    def _check_wifi_capability(self):
        """Check if WiFi tools are available."""
        return shutil.which("iwconfig") is not None or shutil.which("airmon-ng") is not None
    
    def adapt_config(self, config):
        """Adapt configuration for current platform."""
        if self.is_termux:
            config["threads"] = min(config["threads"], 4)  # Limit threads on mobile
            config["color_output"] = True
            config["mobile_ui"] = True
        
        if self.is_kali:
            config["full_features"] = True
            config["use_sudo"] = self.is_root
        
        if self.is_wsl:
            config["network_tools"] = False  # Limited network access in WSL
        
        return config
    
    def get_platform_info(self):
        """Get platform information string."""
        platform_name = []
        if self.is_termux:
            platform_name.append("Termux")
        if self.is_kali:
            platform_name.append("Kali Linux")
        if self.is_wsl:
            platform_name.append("WSL")
        if not platform_name:
            platform_name.append(platform.system())
        
        return " | ".join(platform_name)
```

---

## ONE-COMMAND TEMPLATES

### Template: Security Scanner

```bash
# Install and run in one command
pip install rs-scanner && rs-scanner -t target.com
```

### Template: OSINT Tool

```bash
# Install and run in one command
pip install rs-osint && rs-osint --phone +91XXXXXXXXXX
```

### Template: WiFi Tool

```bash
# Install and run (Kali Linux)
sudo pip install rs-wifi && sudo rs-wifi --scan
```

### Template: Web Scanner

```bash
# Install and run
pip install rs-webscan && rs-webscan -u https://target.com
```

---

## DEPENDENCY DECLARATION

### requirements.txt Template

```
# Core dependencies
requests>=2.28.0
rich>=13.0.0

# Optional dependencies (install with pip install -r requirements-full.txt)
beautifulsoup4>=4.12.0
lxml>=4.9.0
aiohttp>=3.8.0
dnspython>=2.3.0

# Platform-specific
# termux: no additional requirements
# kali: scapy, pwntools (usually pre-installed)
```

### Optional Dependencies

```python
# setup.py
setup(
    # ...
    extras_require={
        "full": ["beautifulsoup4", "lxml", "aiohttp", "dnspython"],
        "dev": ["pytest", "black", "mypy"],
    },
)
```

**Install with:**
```bash
pip install tool-name[full]
```

---

## FIRST-RUN WIZARD

```python
def first_run_wizard():
    """Interactive first-run configuration."""
    config_file = Path.home() / ".rs-tools" / "config" / "[tool]_config.json"
    
    if config_file.exists():
        return json.loads(config_file.read_text())
    
    print("[*] First run detected! Let's configure the tool.\n")
    
    config = {}
    config["api_key"] = input("Enter your API key (or press Enter to skip): ").strip()
    config["output_dir"] = input(f"Output directory [~/.rs-tools/output]: ").strip() or str(Path.home() / ".rs-tools" / "output")
    config["threads"] = int(input("Number of threads [10]: ") or 10)
    
    # Save config
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(config, indent=2))
    
    print(f"\n[+] Configuration saved to {config_file}")
    return config
```

---

## QUICK START COMMANDS

| Tool Type | One Command |
|-----------|-------------|
| Scanner | `pip install rs-scanner && rs-scanner -t target` |
| OSINT | `pip install rs-osint && rs-osint -p +91XXXXXXXXXX` |
| WiFi | `sudo pip install rs-wifi && sudo rs-wifi -s` |
| Web | `pip install rs-webscan && rs-webscan -u URL` |
| Exploit | `pip install rs-exploit && rs-exploit -t target -p port` |
| Recon | `pip install rs-recon && rs-recon -d domain.com` |
