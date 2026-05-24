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
║  VERSION : 2.1.0 GOD MODE NEXUS                                              ║
║  GITHUB  : github.com/T3RMUXK1NG/Downloader                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

🔥 RS DOWNLOADER TOOLKIT v2.1.0 - GOD MODE NEXUS 🔥
   Full Hacker Style Terminal UI | All Features Included
   Termux Compatible | FFmpeg Integration | Modular Architecture
   Multi-Platform Support | Android APK | Docker | Advanced Features
"""

import os
import sys
import time
import json
import subprocess
import threading
import asyncio
import platform
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.colors import *
from utils.banner import show_banner, show_mini_banner, show_about, show_menu_box
from utils.helpers import (
    clear_screen, get_input, press_enter, 
    is_termux, get_downloads_folder, get_system_info, format_size, format_duration
)

# Import modules
from modules import MODULES


class RSDownloaderToolkit:
    """
    RS YouTube Downloader Toolkit - Main Controller
    Author: RS (T3rmuxk1ng)
    Version: 2.1.0 GOD MODE NEXUS
    """

    VERSION = "2.1.0 GOD MODE NEXUS"
    AUTHOR = "RS (RAJSARASWATI JATAV)"
    CHANNEL = "T3rmuxk1ng"
    GITHUB = "github.com/T3RMUXK1NG/Downloader"

    def __init__(self):
        self.running = True
        self.modules = MODULES
        self.config_dir = self._get_config_dir()
        self.config = self._load_config()
        self.download_history = []
        self.session_stats = {
            'downloads': 0,
            'total_size': 0,
            'start_time': datetime.now()
        }

    def _get_config_dir(self) -> str:
        """Get configuration directory"""
        if os.name == 'nt':
            base = os.environ.get('APPDATA', os.path.expanduser('~'))
        elif is_termux():
            base = os.path.expanduser('~')
        else:
            base = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        return os.path.join(base, 'rs_downloader')

    def _load_config(self) -> Dict:
        """Load configuration from file"""
        config_file = os.path.join(self.config_dir, 'config.json')
        default_config = {
            'output_dir': str(get_downloads_folder()),
            'default_video_quality': '1080p',
            'default_audio_quality': '320',
            'parallel_downloads': 3,
            'auto_update': True,
            'notifications': False,
            'theme': 'nexus_green',
            'history_limit': 100,
            'proxy': None
        }
        
        os.makedirs(self.config_dir, exist_ok=True)
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
            except Exception:
                pass
        
        return default_config

    def _save_config(self):
        """Save configuration to file"""
        config_file = os.path.join(self.config_dir, 'config.json')
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def check_dependencies(self) -> bool:
        """Check required dependencies"""
        missing = []
        warnings = []

        # Check Python version
        if sys.version_info < (3, 7):
            print(f"{NEON_RED}[!] Python 3.7+ required (found {sys.version_info.major}.{sys.version_info.minor}){RESET}")
            return False

        print(f"\n{NEON_CYAN}[*] Checking dependencies...{RESET}")

        # Check yt-dlp
        try:
            result = subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"{NEON_GREEN}  ✓ yt-dlp v{version}{RESET}")
            else:
                missing.append('yt-dlp')
        except FileNotFoundError:
            missing.append('yt-dlp')
        except Exception:
            missing.append('yt-dlp')

        # Check FFmpeg
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"{NEON_GREEN}  ✓ FFmpeg detected{RESET}")
            else:
                warnings.append('FFmpeg')
        except FileNotFoundError:
            warnings.append('FFmpeg')
        except Exception:
            warnings.append('FFmpeg')

        # Check for optional tools
        optional_tools = {
            'aria2c': 'aria2 (faster downloads)',
            'atomicparsley': 'AtomicParsley (thumbnail embedding)',
        }

        for tool, desc in optional_tools.items():
            try:
                subprocess.run([tool, '--version'], capture_output=True, timeout=5)
                print(f"{DIM}  + {desc}{RESET}")
            except Exception:
                pass

        if missing:
            print(f"\n{NEON_RED}[!] Missing required dependencies: {', '.join(missing)}{RESET}")
            print(f"\n{NEON_CYAN}[i] Install with:{RESET}")
            print(f"    pip install yt-dlp")
            print(f"\n{NEON_CYAN}[i] For Termux:{RESET}")
            print(f"    pkg install python ffmpeg")
            print(f"    pip install yt-dlp")

            if not self._confirm("\nContinue anyway?", False):
                return False

        if warnings:
            print(f"\n{NEON_YELLOW}[!] Optional features may be limited: {', '.join(warnings)}{RESET}")
            if 'FFmpeg' in warnings:
                print(f"{NEON_CYAN}[i] Install FFmpeg for video merging and conversion:{RESET}")
                if is_termux():
                    print(f"    pkg install ffmpeg")
                elif sys.platform == 'linux':
                    print(f"    sudo apt install ffmpeg")
                elif sys.platform == 'darwin':
                    print(f"    brew install ffmpeg")

        return True

    def _confirm(self, prompt: str, default: bool = False) -> bool:
        """Get yes/no confirmation"""
        default_str = "Y/n" if default else "y/N"
        try:
            response = input(f"{NEON_CYAN}[?] {prompt} ({default_str}): {RESET}").strip().lower()
            if not response:
                return default
            return response in ['y', 'yes', 'true', '1']
        except Exception:
            return default

    def show_main_menu(self):
        """Display main menu"""
        clear_screen()
        show_banner()

        # System status
        info = get_system_info()
        print(f"{DIM}┌─[ {info['os']} {info['architecture']} | Python {info['python']} ]{'─' * 30}┐{RESET}")
        print(f"{DIM}│{' ' * 66}│{RESET}")
        print(f"{DIM}│  Session: {self.session_stats['downloads']} downloads | {format_size(self.session_stats['total_size'])} transferred{' ' * 24}│{RESET}")
        print(f"{DIM}└{'─' * 68}┘{RESET}")

        # Build menu options
        options = []
        for key, (name, _) in self.modules.items():
            options.append((key, name))

        options.append(('0', 'Exit Toolkit'))
        options.append(('00', 'About RS'))
        options.append(('99', 'Settings'))

        show_menu_box("🔱 GOD MODE NEXUS v2.0 🔱", options, "Select module")

    def show_settings(self):
        """Show settings menu"""
        clear_screen()
        print(f"\n{NEON_GREEN}{'═' * 60}{RESET}")
        print(f"{NEON_GREEN}  {'SETTINGS - GOD MODE NEXUS'.center(56)}{RESET}")
        print(f"{NEON_GREEN}{'═' * 60}{RESET}\n")

        print(f"  {NEON_CYAN}[1]{RESET} Output Directory: {BRIGHT_WHITE}{self.config['output_dir']}{RESET}")
        print(f"  {NEON_CYAN}[2]{RESET} Default Video Quality: {BRIGHT_WHITE}{self.config['default_video_quality']}{RESET}")
        print(f"  {NEON_CYAN}[3]{RESET} Default Audio Quality: {BRIGHT_WHITE}{self.config['default_audio_quality']} kbps{RESET}")
        print(f"  {NEON_CYAN}[4]{RESET} Parallel Downloads: {BRIGHT_WHITE}{self.config['parallel_downloads']}{RESET}")
        print(f"  {NEON_CYAN}[5]{RESET} Auto Update: {BRIGHT_WHITE}{'Enabled' if self.config['auto_update'] else 'Disabled'}{RESET}")
        print(f"  {NEON_CYAN}[6]{RESET} Theme: {BRIGHT_WHITE}{self.config['theme']}{RESET}")
        print(f"  {NEON_CYAN}[7]{RESET} Reset to Defaults")
        print(f"  {NEON_CYAN}[0]{RESET} Back to Main Menu")

        choice = input(f"\n{NEON_CYAN}[RS]>{RESET} ").strip()

        if choice == '1':
            new_dir = get_input("Output directory", self.config['output_dir'])
            if new_dir:
                self.config['output_dir'] = new_dir
                self._save_config()
                print(f"{NEON_GREEN}[+] Updated!{RESET}")
                time.sleep(1)
        elif choice == '2':
            qualities = ['4K', '1440p', '1080p', '720p', '480p', '360p', 'best']
            print(f"\n{NEON_CYAN}Select quality:{RESET}")
            for i, q in enumerate(qualities, 1):
                print(f"  [{i}] {q}")
            q_choice = input(f"{NEON_CYAN}[RS]>{RESET} ").strip()
            try:
                self.config['default_video_quality'] = qualities[int(q_choice) - 1]
                self._save_config()
            except (ValueError, IndexError):
                pass
        elif choice == '3':
            qualities = ['320', '256', '192', '128', '96', '64']
            print(f"\n{NEON_CYAN}Select quality (kbps):{RESET}")
            for i, q in enumerate(qualities, 1):
                print(f"  [{i}] {q}")
            q_choice = input(f"{NEON_CYAN}[RS]>{RESET} ").strip()
            try:
                self.config['default_audio_quality'] = qualities[int(q_choice) - 1]
                self._save_config()
            except (ValueError, IndexError):
                pass
        elif choice == '4':
            new_val = get_input("Parallel downloads (1-10)", str(self.config['parallel_downloads']))
            try:
                self.config['parallel_downloads'] = max(1, min(10, int(new_val)))
                self._save_config()
            except ValueError:
                pass
        elif choice == '5':
            self.config['auto_update'] = not self.config['auto_update']
            self._save_config()
        elif choice == '6':
            themes = ['nexus_green', 'matrix', 'cyberpunk', 'classic']
            print(f"\n{NEON_CYAN}Select theme:{RESET}")
            for i, t in enumerate(themes, 1):
                print(f"  [{i}] {t}")
            t_choice = input(f"{NEON_CYAN}[RS]>{RESET} ").strip()
            try:
                self.config['theme'] = themes[int(t_choice) - 1]
                self._save_config()
            except (ValueError, IndexError):
                pass
        elif choice == '7':
            if self._confirm("Reset all settings to defaults?"):
                self.config = {
                    'output_dir': str(get_downloads_folder()),
                    'default_video_quality': '1080p',
                    'default_audio_quality': '320',
                    'parallel_downloads': 3,
                    'auto_update': True,
                    'notifications': False,
                    'theme': 'nexus_green',
                    'history_limit': 100,
                    'proxy': None
                }
                self._save_config()
                print(f"{NEON_GREEN}[+] Settings reset!{RESET}")
                time.sleep(1)

    def show_about_screen(self):
        """Show about screen"""
        clear_screen()
        show_about()

        info = get_system_info()
        
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'SYSTEM INFORMATION'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}OS:{RESET} {BRIGHT_WHITE}{info['os']} {info['architecture']}{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}Python:{RESET} {BRIGHT_WHITE}{info['python']}{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}Termux:{RESET} {BRIGHT_WHITE}{'Yes' if info['termux'] else 'No'}{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}Downloads:{RESET} {BRIGHT_WHITE}{info['downloads_folder']}{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}Config:{RESET} {BRIGHT_WHITE}{self.config_dir}{RESET}")
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")

        print(f"\n{NEON_CYAN}{'─' * 60}{RESET}")
        print(f"{NEXUS_GOLD}  GOD MODE NEXUS v2.0 Features:{RESET}")
        print(f"{NEON_GREEN}  • Multi-platform support (YouTube, Twitch, Twitter, etc.){RESET}")
        print(f"{NEON_GREEN}  • 4K/8K video downloads with HDR support{RESET}")
        print(f"{NEON_GREEN}  • Advanced audio extraction with metadata embedding{RESET}")
        print(f"{NEON_GREEN}  • Playlist and batch download with parallel processing{RESET}")
        print(f"{NEON_GREEN}  • Real-time progress tracking with speed/ETA{RESET}")
        print(f"{NEON_GREEN}  • Subtitle download in multiple formats{RESET}")
        print(f"{NEON_GREEN}  • Thumbnail extraction and embedding{RESET}")
        print(f"{NEON_GREEN}  • Media conversion with FFmpeg integration{RESET}")
        print(f"{NEON_GREEN}  • Search and download directly from terminal{RESET}")
        print(f"{NEON_GREEN}  • Proxy and authentication support{RESET}")
        print(f"{NEON_CYAN}{'─' * 60}{RESET}")

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
                # Update session stats
                self.session_stats['downloads'] += 1
            except Exception as e:
                print(f"\n{NEON_RED}[!] Error: {e}{RESET}")
                import traceback
                traceback.print_exc()
                press_enter()
        else:
            print(f"{NEON_RED}[!] Invalid option{RESET}")
            time.sleep(1)

    def update_yt_dlp(self):
        """Update yt-dlp to latest version"""
        print(f"\n{NEON_CYAN}[*] Updating yt-dlp...{RESET}")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"{NEON_GREEN}[+] yt-dlp updated successfully!{RESET}")
            else:
                print(f"{NEON_RED}[!] Update failed{RESET}")
        except Exception as e:
            print(f"{NEON_RED}[!] Error: {e}{RESET}")
        time.sleep(2)

    def exit_toolkit(self):
        """Exit toolkit with style"""
        self.running = False
        clear_screen()
        show_mini_banner()

        # Session summary
        elapsed = datetime.now() - self.session_stats['start_time']
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}🙏 THANK YOU FOR USING RS DOWNLOADER TOOLKIT 🙏{RESET}".center(70))
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}Session Summary:{RESET}")
        print(f"{NEON_GREEN}║{RESET}    {BRIGHT_WHITE}Downloads: {self.session_stats['downloads']}{RESET}")
        print(f"{NEON_GREEN}║{RESET}    {BRIGHT_WHITE}Data Transfer: {format_size(self.session_stats['total_size'])}{RESET}")
        print(f"{NEON_GREEN}║{RESET}    {BRIGHT_WHITE}Session Time: {hours:02d}:{minutes:02d}:{seconds:02d}{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}YouTube :{RESET} {BRIGHT_WHITE}@T3rmuxk1ng{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}GitHub  :{RESET} {BRIGHT_WHITE}{self.GITHUB}{RESET}")
        print(f"{NEON_GREEN}║{RESET}  {CYAN}Version :{RESET} {BRIGHT_WHITE}{self.VERSION}{RESET}")
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}\n")

        print(f"{NEXUS_GOLD}🔱 GOD MODE NEXUS - POWER UNLEASHED 🔱{RESET}")
        print(f"{NEON_CYAN}[*] Exiting... See you soon! 🔥{RESET}\n")
        sys.exit(0)

    def run(self):
        """Main entry point"""
        # Check dependencies
        if not self.check_dependencies():
            return

        # Auto-update check
        if self.config.get('auto_update', False):
            try:
                result = subprocess.run(
                    ['yt-dlp', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                # Silent check, don't bother user
            except Exception:
                pass

        # Main loop
        while self.running:
            try:
                self.show_main_menu()

                choice = input(f"{NEON_GREEN}[RS]>{RESET} ").strip()

                if choice == '0':
                    self.exit_toolkit()
                elif choice == '00':
                    self.show_about_screen()
                elif choice == '99':
                    self.show_settings()
                elif choice == 'update':
                    self.update_yt_dlp()
                elif choice in self.modules:
                    self.run_module(choice)
                else:
                    print(f"{NEON_RED}[!] Invalid option: {choice}{RESET}")
                    time.sleep(1)

            except KeyboardInterrupt:
                print(f"\n{NEON_YELLOW}[!] Press '0' to exit gracefully{RESET}")
                time.sleep(1)
            except EOFError:
                print(f"\n{NEON_YELLOW}[!] EOF received, exiting...{RESET}")
                self.running = False
            except Exception as e:
                print(f"{NEON_RED}[!] Error: {e}{RESET}")
                time.sleep(2)


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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
