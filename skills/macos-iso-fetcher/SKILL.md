---
name: macos-iso-fetcher
description: Download and create bootable macOS ISO images for Hackintosh or Virtual Machines. Use this skill whenever the user asks for macOS ISO, Hackintosh download, macOS VM image, macOS installer, or wants to install macOS on non-Apple hardware. This skill searches for legitimate download sources, generates scripts to create bootable images, and provides complete setup guidance for VirtualBox, VMware, or Hackintosh installations.
---

# macOS ISO Fetcher Skill

## Mission

Download and create bootable macOS ISO/DMG images for Hackintosh installations or Virtual Machine usage. This skill provides legitimate methods, direct download links, and automated scripts.

## IMPORTANT RULES

1. **ALWAYS try multiple sources** - Never give up on the first failure
2. **Keep trying until success** - Search, scrape, automate, whatever it takes
3. **Provide working solutions** - Test and verify download links
4. **Generate automation scripts** - Python/Bash scripts to automate the process
5. **NO giving up** - If one method fails, try another

## macOS Versions Available

| Version | Codename | Year | Status |
|---------|----------|------|--------|
| macOS 15 | Sequoia | 2024 | Latest |
| macOS 14 | Sonoma | 2023 | Supported |
| macOS 13 | Ventura | 2022 | Supported |
| macOS 12 | Monterey | 2021 | Supported |
| macOS 11 | Big Sur | 2020 | Supported |
| macOS 10.15 | Catalina | 2019 | Supported |
| macOS 10.14 | Mojave | 2018 | Legacy |

## Primary Methods

### Method 1: Apple Official Recovery Images (RECOMMENDED)

Apple provides recovery images through their servers. Use these tools:

```bash
# gibMacOS - Downloads from Apple directly
git clone https://github.com/corpnewt/gibMacOS
cd gibMacOS
python gibMacOS.command
```

### Method 2: OpenCore Legacy Patcher

```bash
# Download macOS via OCLP
# https://dortania.github.io/OpenCore-Legacy-Patcher/
```

### Method 3: mist-cli (macOS only)

```bash
brew install mist-cli
mist download installer "Sonoma" --output-directory ~/Downloads
```

### Method 4: Archive.org (Pre-made images)

Search archive.org for macOS ISO images created by community.

### Method 5: Direct DMG Links

Various legitimate sources provide direct DMG downloads from Apple's CDN.

## Output Requirements

1. **Search for download sources** - Use web search extensively
2. **Generate Python automation script** - Create a script that downloads and converts
3. **Provide step-by-step instructions** - Clear guidance for the user
4. **Create bootable USB guide** - How to use the downloaded image

## Script Template

When generating download scripts, use this pattern:

```python
#!/usr/bin/env python3
"""
macOS ISO Downloader and Creator
Automatically downloads macOS and creates bootable ISO
"""

import os
import subprocess
import urllib.request
import json

# Configuration
MACOS_VERSION = "Ventura"  # Change as needed
OUTPUT_DIR = "/home/z/my-project/download/"

def download_macos():
    # Implementation
    pass

def create_iso():
    # Implementation
    pass

if __name__ == "__main__":
    download_macos()
    create_iso()
```

## Verification Checklist

After creating any solution:

- [ ] Download link verified working
- [ ] File size reasonable (macOS is ~12-15GB)
- [ ] Instructions clear and complete
- [ ] Alternative methods provided if primary fails

## Never Give Up Protocol

If initial searches fail:

1. Try different search queries
2. Search archive.org specifically
3. Search GitHub for download scripts
4. Provide gibMacOS method as fallback
5. Create manual download instructions

## Final Output

Always save the final ISO/image to:
`/home/z/my-project/download/macos-{version}.iso`

Or provide direct download links that the user can use.
