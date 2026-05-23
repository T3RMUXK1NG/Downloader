#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Banner Display                              ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import random
import sys
from .colors import *


# Main Banners
BANNERS = [
    r'''
   ██████╗ ███████╗██████╗     ███████╗████████╗██████╗ █████╗ ███████╗███████╗
   ██╔══██╗██╔════╝██╔══██╗    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝
   ██████╔╝███████╗██████╔╝    ███████╗   ██║   ██████╔╝███████║███████╗█████╗  
   ██╔══██╗╚════██║██╔══██╗    ╚════██║   ██║   ██╔══██╗██╔══██║╚════██║██╔══╝  
   ██║  ██║███████║██████╔╝    ███████║   ██║   ██║  ██║██║  ██║███████║███████╗
   ╚═╝  ╚═╝╚══════╝╚═════╝     ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝

   ███████╗██╗   ██╗███████╗████████╗███████╗██████╗                            
   ██╔════╝██║   ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗                           
   █████╗  ██║   ██║███████╗   ██║   █████╗  ██████╔╝                           
   ██╔══╝  ██║   ██║╚════██║   ██║   ██╔══╝  ██╔══██╗                           
   ██║     ╚██████╔╝███████║   ██║   ███████╗██║  ██║                           
   ╚═╝      ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                           
''',
    r'''
   ╔══════════════════════════════════════════════════════════════════════════════╗
   ║                                                                              ║
   ║   ██████╗ ███████╗██████╗     ███████╗████████╗██████╗ █████╗ ███████╗      ║
   ║   ██╔══██╗██╔════╝██╔══██╗    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝      ║
   ║   ██████╔╝███████╗██████╔╝    ███████╗   ██║   ██████╔╝███████║███████╗      ║
   ║   ██╔══██╗╚════██║██╔══██╗    ╚════██║   ██║   ██╔══██╗██╔══██║╚════██║      ║
   ║   ██║  ██║███████║██████╔╝    ███████║   ██║   ██║  ██║██║  ██║███████║      ║
   ║   ╚═╝  ╚═╝╚══════╝╚═════╝     ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝      ║
   ║                                                                              ║
   ╠══════════════════════════════════════════════════════════════════════════════╣
   ║                     🔥 RS DOWNLOADER TOOLKIT 🔥                              ║
   ╚══════════════════════════════════════════════════════════════════════════════╝
''',
]

# Mini Banner
MINI_BANNER = r'''
   ╔═════════════════════════════════════════╗
   ║   🔥 RS DOWNLOADER TOOLKIT v1.0.0 🔥   ║
   ║   Author: T3rmuxk1ng                   ║
   ╚═════════════════════════════════════════╝
'''

# About Banner
ABOUT_BANNER = r'''
   ╔═══════════════════════════════════════════════════════════════╗
   ║                                                               ║
   ║     ██████╗ ███████╗██████╗                                   ║
   ║     ██╔══██╗██╔════╝██╔══██╗                                  ║
   ║     ██████╔╝███████╗██████╔╝                                  ║
   ║     ██╔══██╗╚════██║██╔══██╗                                  ║
   ║     ██║  ██║███████║██████╔╝                                  ║
   ║     ╚═╝  ╚═╝╚══════╝╚═════╝                                   ║
   ║                                                               ║
   ║     ██████╗  █████╗ ██████╗ ██████╗                           ║
   ║     ██╔══██╗██╔══██╗██╔══██╗██╔══██╗                          ║
   ║     ██████╔╝███████║██████╔╝██║  ██║                          ║
   ║     ██╔══██╗██╔══██║██╔══██╗██║  ██║                          ║
   ║     ██║  ██║██║  ██║██████╔╝██████╔╝                          ║
   ║     ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═════╝                           ║
   ║                                                               ║
   ╠═══════════════════════════════════════════════════════════════╣
   ║  AUTHOR   : RAJSARASWATI JATAV (RS)                           ║
   ║  CHANNEL  : T3rmuxk1ng (YouTube)                              ║
   ║  GITHUB   : github.com/T3RMUXK1NG                             ║
   ║  VERSION  : 1.0.0 GOD MODE EDITION                            ║
   ║  STATUS   : 🔥 LEGENDARY EXPERT 🔥                            ║
   ╚═══════════════════════════════════════════════════════════════╝
'''


def get_terminal_width() -> int:
    """Get terminal width"""
    try:
        return os.get_terminal_size().columns
    except Exception:
        return 80


def show_banner():
    """Display random hacker-style banner"""
    banner = random.choice(BANNERS)

    # Print banner with color
    print(f"\n{NEON_GREEN}{banner}{RESET}")

    # Display branding info
    width = get_terminal_width()
    line = '═' * (width - 4)

    print(f"{NEON_CYAN}{line}{RESET}")
    print(f"{NEON_GREEN}  AUTHOR  : {BRIGHT_WHITE}RS (RAJSARASWATI JATAV){RESET}")
    print(f"{NEON_GREEN}  CHANNEL : {BRIGHT_WHITE}T3rmuxk1ng (YouTube){RESET}")
    print(f"{NEON_GREEN}  VERSION : {BRIGHT_WHITE}1.0.0 GOD MODE EDITION{RESET}")
    print(f"{NEON_GREEN}  GITHUB  : {BRIGHT_WHITE}github.com/T3RMUXK1NG/Downloader{RESET}")
    print(f"{NEON_CYAN}{line}{RESET}")


def show_mini_banner():
    """Display compact mini banner"""
    print(f"\n{NEON_GREEN}{MINI_BANNER}{RESET}")


def show_about():
    """Display about banner"""
    print(f"\n{NEON_GREEN}{ABOUT_BANNER}{RESET}")


def show_module_header(module_name: str, icon: str = "▶"):
    """Display module header"""
    width = get_terminal_width()
    line = '═' * (width - 4)

    print(f"\n{NEON_GREEN}{line}{RESET}")
    print(f"{NEON_GREEN}  {icon} {BRIGHT_WHITE}{module_name.center(width - 8)}{RESET} {icon}")
    print(f"{NEON_GREEN}{line}{RESET}\n")


def show_menu_box(title: str, options: list, prompt: str = "Select option"):
    """Display menu in a box"""
    width = 60

    print(f"\n{NEON_GREEN}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{title.center(width - 4)}{RESET} {NEON_GREEN}║{RESET}")
    print(f"{NEON_GREEN}╠{'═' * (width - 2)}╣{RESET}")

    for key, label in options:
        line = f"  [{CYAN}{key}{RESET}] {label}"
        padding = width - 4 - len(line) + len(key) * 2 + 10
        print(f"{NEON_GREEN}║{RESET}{line}{' ' * max(0, padding)}{NEON_GREEN}║{RESET}")

    print(f"{NEON_GREEN}╚{'═' * (width - 2)}╝{RESET}")
    print(f"\n{NEON_CYAN}[RS]>{RESET} {BRIGHT_WHITE}{prompt}: {RESET}", end="")


def show_error_box(title: str, message: str):
    """Display error in a box"""
    width = max(len(title), len(message)) + 6

    print(f"\n{NEON_RED}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{NEON_RED}║{RESET} {BRIGHT_WHITE}{title.center(width - 4)}{RESET} {NEON_RED}║{RESET}")
    print(f"{NEON_RED}╠{'═' * (width - 2)}╣{RESET}")
    print(f"{NEON_RED}║{RESET} {message.center(width - 4)} {NEON_RED}║{RESET}")
    print(f"{NEON_RED}╚{'═' * (width - 2)}╝{RESET}\n")


def show_success_box(title: str, message: str):
    """Display success in a box"""
    width = max(len(title), len(message)) + 6

    print(f"\n{NEON_GREEN}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{title.center(width - 4)}{RESET} {NEON_GREEN}║{RESET}")
    print(f"{NEON_GREEN}╠{'═' * (width - 2)}╣{RESET}")
    print(f"{NEON_GREEN}║{RESET} {message.center(width - 4)} {NEON_GREEN}║{RESET}")
    print(f"{NEON_GREEN}╚{'═' * (width - 2)}╝{RESET}\n")


def show_loading(message: str = "Loading"):
    """Show loading animation"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    for frame in frames:
        sys.stdout.write(f"\r{NEON_CYAN}{frame}{RESET} {message}...")
        sys.stdout.flush()
        import time
        time.sleep(0.1)

    sys.stdout.write(f"\r{NEON_GREEN}✓{RESET} {message} complete!   \n")
