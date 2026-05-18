#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Module 6: Subtitle Downloader               ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader_base import DownloaderBase
from utils.colors import *
from utils.banner import show_module_header, show_error_box, show_success_box
from utils.helpers import get_input, confirm, press_enter
from utils.validator import URLValidator, get_video_id


class SubtitleDownloader(DownloaderBase):
    """
    Subtitle Downloader Module
    - Download video subtitles
    - Multiple languages
    - Auto-generated support
    - SRT/VTT/TXT formats
    """
    
    FORMATS = [
        ('1', 'SRT (Most Compatible)', 'srt'),
        ('2', 'VTT (Web)', 'vtt'),
        ('3', 'TXT (Plain Text)', 'ttml'),
    ]
    
    COMMON_LANGUAGES = [
        ('1', 'English', 'en'),
        ('2', 'Hindi', 'hi'),
        ('3', 'Spanish', 'es'),
        ('4', 'French', 'fr'),
        ('5', 'German', 'de'),
        ('6', 'Japanese', 'ja'),
        ('7', 'Korean', 'ko'),
        ('8', 'Portuguese', 'pt'),
        ('9', 'Russian', 'ru'),
        ('10', 'Arabic', 'ar'),
        ('11', 'All Available', 'all'),
    ]
    
    def __init__(self):
        super().__init__()
        self.name = "Subtitle Downloader"
        self.module_icon = "📝"
    
    def run(self):
        """Run subtitle downloader module"""
        show_module_header(f"{self.module_icon} SUBTITLE DOWNLOADER", "▶")
        
        # Get URL
        print(f"{NEON_CYAN}[?] Enter YouTube Video URL (or 'back' to return):{RESET}")
        url = get_input("URL")
        
        if url.lower() == 'back':
            return
        
        # Validate
        video_id = get_video_id(url)
        if not video_id:
            show_error_box("Invalid URL", "Please enter a valid YouTube URL")
            return
        
        # Get available subtitles
        print(f"\n{NEON_GREEN}[+] Checking available subtitles...{RESET}")
        subtitles = self._get_available_subtitles(url)
        
        if not subtitles:
            show_error_box("No Subtitles", "No subtitles available for this video")
            return
        
        # Display available subtitles
        self._display_available_subtitles(subtitles)
        
        # Get options
        options = self._get_options()
        
        # Download
        self._download_subtitles(url, options)
    
    def _get_available_subtitles(self, url: str) -> Dict:
        """Get list of available subtitles"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--list-subs', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return self._parse_subtitle_list(result.stdout)
                
        except:
            pass
        
        return {}
    
    def _parse_subtitle_list(self, output: str) -> Dict:
        """Parse subtitle list from yt-dlp output"""
        subtitles = {
            'manual': [],
            'auto': []
        }
        
        lines = output.split('\n')
        
        current_section = None
        for line in lines:
            if 'Available subtitles' in line:
                current_section = 'manual'
            elif 'Automatic captions' in line:
                current_section = 'auto'
            elif line.strip() and current_section:
                parts = line.split()
                if len(parts) >= 2:
                    lang_code = parts[0]
                    lang_name = ' '.join(parts[1:]) if len(parts) > 1 else lang_code
                    
                    if current_section == 'manual':
                        subtitles['manual'].append({
                            'code': lang_code,
                            'name': lang_name
                        })
                    else:
                        subtitles['auto'].append({
                            'code': lang_code,
                            'name': lang_name
                        })
        
        return subtitles
    
    def _display_available_subtitles(self, subtitles: Dict):
        """Display available subtitles"""
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'AVAILABLE SUBTITLES'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        
        if subtitles['manual']:
            print(f"{NEON_GREEN}║{RESET} {NEON_CYAN}Manual Subtitles:{RESET}")
            for sub in subtitles['manual'][:10]:
                print(f"{NEON_GREEN}║{RESET}   {BRIGHT_WHITE}{sub['code']}{RESET} - {sub['name'][:30]}")
        
        if subtitles['auto']:
            print(f"{NEON_GREEN}║{RESET}")
            print(f"{NEON_GREEN}║{RESET} {NEON_CYAN}Auto-Generated:{RESET}")
            for sub in subtitles['auto'][:5]:
                print(f"{NEON_GREEN}║{RESET}   {BRIGHT_WHITE}{sub['code']}{RESET} - {sub['name'][:30]}")
        
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")
    
    def _get_options(self) -> Dict:
        """Get download options"""
        options = {}
        
        # Language
        print(f"\n{NEON_CYAN}[?] Select Language:{RESET}\n")
        for key, label, _ in self.COMMON_LANGUAGES:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")
        
        lang_choice = get_input("Language", "1")
        
        for key, label, value in self.COMMON_LANGUAGES:
            if lang_choice == key:
                options['language'] = value
                break
        else:
            options['language'] = 'en'
        
        # Format
        print(f"\n{NEON_CYAN}[?] Select Subtitle Format:{RESET}\n")
        for key, label, _ in self.FORMATS:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")
        
        format_choice = get_input("Format", "1")
        
        for key, label, value in self.FORMATS:
            if format_choice == key:
                options['format'] = value
                break
        else:
            options['format'] = 'srt'
        
        # Auto-generated
        options['include_auto'] = confirm("Include auto-generated?", True)
        
        return options
    
    def _download_subtitles(self, url: str, options: Dict):
        """Download subtitles"""
        output_dir = self.create_output_dir('subtitles')
        
        # Get video info for filename
        video_id = get_video_id(url)
        
        print(f"\n{NEON_GREEN}[+] Downloading subtitles...{RESET}")
        print(f"{NEON_CYAN}[→] Language: {options['language']}{RESET}")
        print(f"{NEON_CYAN}[→] Format: {options['format']}{RESET}")
        
        # Build command
        cmd = self._build_command(url, output_dir, options)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                show_success_box("SUCCESS", f"Subtitles saved to:\n{output_dir}")
            else:
                show_error_box("Error", f"Could not download subtitles.\n{result.stderr}")
                
        except Exception as e:
            show_error_box("Error", str(e))
        
        press_enter()
    
    def _build_command(self, url: str, output_dir: str, options: Dict) -> list:
        """Build yt-dlp command"""
        cmd = ['yt-dlp']
        
        # Write subtitles
        cmd.append('--write-subs')
        
        # Include auto-generated
        if options.get('include_auto'):
            cmd.append('--write-auto-subs')
        
        # Language
        lang = options.get('language', 'en')
        if lang != 'all':
            cmd.extend(['--sub-langs', lang])
        else:
            cmd.extend(['--sub-langs', 'all'])
        
        # Format
        sub_format = options.get('format', 'srt')
        cmd.extend(['--sub-format', sub_format])
        
        # Convert to chosen format
        cmd.extend(['--convert-subs', sub_format])
        
        # Output
        output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
        cmd.extend(['-o', output_template])
        
        # Skip video download
        cmd.append('--skip-download')
        
        # URL
        cmd.append(url)
        
        return cmd
    
    def download(self, url: str, language: str = 'en', sub_format: str = 'srt',
                 include_auto: bool = True, output_dir: str = None) -> Tuple[bool, str]:
        """Programmatic download"""
        video_id = get_video_id(url)
        if not video_id:
            return False, "Invalid YouTube URL"
        
        if output_dir is None:
            output_dir = self.create_output_dir('subtitles')
        
        options = {
            'language': language,
            'format': sub_format,
            'include_auto': include_auto
        }
        
        cmd = self._build_command(url, output_dir, options)
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode == 0:
                return True, output_dir
            return False, result.stderr.decode()
        except Exception as e:
            return False, str(e)


def run():
    """Run subtitle downloader"""
    downloader = SubtitleDownloader()
    downloader.run()


if __name__ == "__main__":
    run()
