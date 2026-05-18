#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ███████╗██████╗     ███████╗████████╗██████╗ █████╗ ███████╗███████╗║
║   ██╔══██╗██╔════╝██╔══██╗    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝║
║   ██████╔╝███████╗██████╔╝    ███████╗   ██║   ██████╔╝███████║███████╗█████╗  ║
║   ██╔══██╗╚════██║██╔══██╗    ╚════██║   ██║   ██╔══██╗██╔══██║╚════██║██╔══╝  ║
║   ██║  ██║███████║██████╔╝    ███████║   ██║   ██║  ██║██║  ██║███████║███████╗║
║   ╚═╝  ╚═╝╚══════╝╚═════╝     ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝║
║                                                                              ║
║   ███████╗██╗   ██╗███████╗████████╗███████╗██████╗                          ║
║   ██╔════╝██║   ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗                         ║
║   █████╗  ██║   ██║███████╗   ██║   █████╗  ██████╔╝                         ║
║   ██╔══╝  ██║   ██║╚════██║   ██║   ██╔══╝  ██╔══██╗                         ║
║   ██║     ╚██████╔╝███████║   ██║   ███████╗██║  ██║                         ║
║   ╚═╝      ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                         ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  AUTHOR  : RS (RAJSARASWATI JATAV)                                           ║
║  CHANNEL : T3rmuxk1ng (YouTube)                                              ║
║  VERSION : 1.0.0 GOD MODE EDITION                                            ║
║  GITHUB  : github.com/T3RMUXK1NG/Downloader                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

🔥 RS DOWNLOADER TOOLKIT - LEGENDARY YOUTUBE DOWNLOADER 🔥
   Full Hacker Style Terminal UI | All Features Included
   Termux Compatible | FFmpeg Integration | Modular Architecture
"""

import os
import sys
import time
import subprocess
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.colors import *
from utils.banner import show_banner, show_mini_banner, show_about, show_menu_box
from utils.helpers import (
    clear_screen, get_input, press_enter, 
    is_termux, get_downloads_folder, get_system_info
)

# Import modules
from modules import MODULES


class RSDownloaderToolkit:
    """
    RS YouTube Downloader Toolkit - Main Controller
    Author: RS (T3rmuxk1ng)
    Version: 1.0.0 GOD MODE EDITION
    """
    
    VERSION = "1.0.0 GOD MODE EDITION"
    AUTHOR = "RS (RAJSARASWATI JATAV)"
    CHANNEL = "T3rmuxk1ng"
    GITHUB = "github.com/T3RMUXK1NG/Downloader"
    
    def __init__(self):
        self.running = True
        self.modules = MODULES
        
    def check_dependencies(self) -> bool:
        """Check required dependencies"""
        missing = []
        
        # Check Python version
        if sys.version_info < (3, 6):
            print(f"{NEON_RED}[!] Python 3.6+ required{RESET}")
            return False
        
        # Check yt-dlp
        try:
            result = subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                missing.append('yt-dlp')
        except FileNotFoundError:
            missing.append('yt-dlp')
        
        # Check FFmpeg (optional but recommended)
        ffmpeg_available = False
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True
            )
            ffmpeg_available = result.returncode == 0
        except FileNotFoundError:
            pass
        
        if missing:
            print(f"\n{NEON_YELLOW}[!] Missing dependencies: {', '.join(missing)}{RESET}")
            print(f"\n{NEON_CYAN}[i] Install with:{RESET}")
            print(f"    pip install yt-dlp")
            print(f"\n{NEON_CYAN}[i] For FFmpeg (optional but recommended):{RESET}")
            if is_termux():
                print(f"    pkg install ffmpeg")
            elif sys.platform == 'linux':
                print(f"    sudo apt install ffmpeg")
            elif sys.platform == 'darwin':
                print(f"    brew install ffmpeg")
            
            if not confirm("\nContinue anyway?", True):
                return False
        
        return True
    
    def show_main_menu(self):
        """Display main menu"""
        clear_screen()
        show_banner()
        
        # Build menu options
        options = []
        for key, (name, _) in self.modules.items():
            options.append((key, name))
        
        options.append(('0', 'Exit Toolkit'))
        options.append(('00', 'About RS'))
        
        show_menu_box("SELECT MODULE", options, "Select module")
    
    def show_about_screen(self):
        """Show about screen"""
        clear_screen()
        show_about()
        
        print(f"\n{NEON_CYAN}System Information:{RESET}")
        info = get_system_info()
        print(f"  OS: {info['os']} {info['architecture']}")
        print(f"  Python: {info['python']}")
        print(f"  Termux: {'Yes' if info['termux'] else 'No'}")
        print(f"  Downloads: {info['downloads_folder']}")
        
        press_enter()
    
    def run_module(self, choice: str):
        """Run selected module"""
        if choice in self.modules:
            name, module_class = self.modules[choice]
            print(f"\n{NEON_GREEN}[+] Loading {name}...{RESET}")
            time.sleep(0.3)
            
            try:
                module = module_class()
                module.run()
            except Exception as e:
                print(f"\n{NEON_RED}[!] Error: {e}{RESET}")
                press_enter()
        else:
            print(f"{NEON_RED}[!] Invalid option{RESET}")
            time.sleep(1)
    
    def exit_toolkit(self):
        """Exit toolkit with style"""
        self.running = False
        clear_screen()
        show_mini_banner()
        
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}🙏 THANK YOU FOR USING RS DOWNLOADER TOOLKIT 🙏{RESET}".center(70))
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}YouTube :{RESET} {BRIGHT_WHITE}@T3rmuxk1ng{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}GitHub  :{RESET} {BRIGHT_WHITE}{self.GITHUB}{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}Version :{RESET} {BRIGHT_WHITE}{self.VERSION}{RESET}")
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}\n")
        
        print(f"{NEON_CYAN}[*] Exiting... See you soon! 🔥{RESET}\n")
        sys.exit(0)
    
    def run(self):
        """Main entry point"""
        # Check dependencies
        if not self.check_dependencies():
            return
        
        # Main loop
        while self.running:
            try:
                self.show_main_menu()
                
                choice = input(f"{NEON_GREEN}[RS]>{RESET} ").strip()
                
                if choice == '0':
                    self.exit_toolkit()
                elif choice == '00':
                    self.show_about_screen()
                elif choice in self.modules:
                    self.run_module(choice)
                else:
                    print(f"{NEON_RED}[!] Invalid option: {choice}{RESET}")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print(f"\n{NEON_YELLOW}[!] Press '0' to exit{RESET}")
                time.sleep(1)
            except Exception as e:
                print(f"{NEON_RED}[!] Error: {e}{RESET}")
                time.sleep(2)


def confirm(prompt: str, default: bool = False) -> bool:
    """Get yes/no confirmation"""
    default_str = "Y/n" if default else "y/N"
    try:
        response = input(f"{NEON_CYAN}[?] {prompt} ({default_str}): {RESET}").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes', 'true', '1']
    except:
        return default


def main():
    """Main function"""
    try:
        toolkit = RSDownloaderToolkit()
        toolkit.run()
    except KeyboardInterrupt:
        print(f"\n{NEON_YELLOW}[!] Interrupted by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{NEON_RED}[FATAL ERROR] {e}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
