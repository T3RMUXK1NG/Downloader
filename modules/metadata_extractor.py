#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Module 5: Metadata Extractor                ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import subprocess
from typing import Dict, Optional, List
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader_base import DownloaderBase
from utils.colors import *
from utils.banner import show_module_header, show_error_box, show_success_box
from utils.helpers import get_input, confirm, press_enter, format_size, format_number
from utils.validator import URLValidator, get_video_id


class MetadataExtractor(DownloaderBase):
    """
    Metadata Extractor Module
    - Extract video information
    - Channel details
    - Technical metadata
    - Export to JSON/TXT/CSV
    """
    
    EXPORT_FORMATS = [
        ('1', 'JSON', 'json'),
        ('2', 'TXT (Text)', 'txt'),
        ('3', 'CSV', 'csv'),
    ]
    
    def __init__(self):
        super().__init__()
        self.name = "Metadata Extractor"
        self.module_icon = "📊"
    
    def run(self):
        """Run metadata extractor module"""
        show_module_header(f"{self.module_icon} METADATA EXTRACTOR", "▶")
        
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
        
        # Get metadata
        print(f"\n{NEON_GREEN}[+] Extracting metadata...{RESET}")
        metadata = self._extract_metadata(url)
        
        if not metadata:
            show_error_box("Error", "Could not extract metadata")
            return
        
        # Display metadata
        self._display_metadata(metadata)
        
        # Export option
        if confirm("Export metadata?", True):
            self._export_metadata(metadata)
        
        press_enter()
    
    def _extract_metadata(self, url: str) -> Optional[Dict]:
        """Extract video metadata using yt-dlp"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-download', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                raw_data = json.loads(result.stdout)
                return self._parse_metadata(raw_data)
                
        except:
            pass
        
        return None
    
    def _parse_metadata(self, raw: Dict) -> Dict:
        """Parse raw metadata into structured format"""
        return {
            # Basic Info
            'id': raw.get('id', 'N/A'),
            'title': raw.get('title', 'N/A'),
            'description': raw.get('description', 'N/A'),
            'duration': raw.get('duration', 0),
            'duration_string': raw.get('duration_string', 'N/A'),
            
            # Upload Info
            'uploader': raw.get('uploader', 'N/A'),
            'uploader_id': raw.get('uploader_id', 'N/A'),
            'uploader_url': raw.get('uploader_url', 'N/A'),
            'channel': raw.get('channel', 'N/A'),
            'channel_id': raw.get('channel_id', 'N/A'),
            'channel_url': raw.get('channel_url', 'N/A'),
            
            # Stats
            'view_count': raw.get('view_count', 0),
            'like_count': raw.get('like_count', 0),
            'comment_count': raw.get('comment_count', 0),
            
            # Dates
            'upload_date': raw.get('upload_date', 'N/A'),
            'timestamp': raw.get('timestamp', 0),
            'release_date': raw.get('release_date', 'N/A'),
            
            # Technical
            'width': raw.get('width', 0),
            'height': raw.get('height', 0),
            'fps': raw.get('fps', 0),
            'vcodec': raw.get('vcodec', 'N/A'),
            'acodec': raw.get('acodec', 'N/A'),
            'ext': raw.get('ext', 'N/A'),
            'filesize': raw.get('filesize', 0) or raw.get('filesize_approx', 0),
            
            # Categories & Tags
            'categories': raw.get('categories', []),
            'tags': raw.get('tags', []),
            
            # URLs
            'webpage_url': raw.get('webpage_url', 'N/A'),
            'thumbnail': raw.get('thumbnail', 'N/A'),
            
            # Other
            'availability': raw.get('availability', 'N/A'),
            'live_status': raw.get('live_status', 'N/A'),
            'age_limit': raw.get('age_limit', 0),
        }
    
    def _display_metadata(self, meta: Dict):
        """Display formatted metadata"""
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'VIDEO METADATA'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        
        # Basic Info
        print(f"{NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}║{RESET} {NEON_CYAN}{'─' * 20} BASIC INFO {'─' * 20}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}ID:{RESET} {BRIGHT_WHITE}{meta['id']}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Title:{RESET} {BRIGHT_WHITE}{meta['title'][:50]}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Duration:{RESET} {BRIGHT_WHITE}{meta['duration_string']}{RESET}")
        
        # Channel Info
        print(f"{NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}║{RESET} {NEON_CYAN}{'─' * 20} CHANNEL {'─' * 23}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Channel:{RESET} {BRIGHT_WHITE}{meta['channel'][:40]}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Channel ID:{RESET} {BRIGHT_WHITE}{meta['channel_id']}{RESET}")
        
        # Stats
        print(f"{NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}║{RESET} {NEON_CYAN}{'─' * 20} STATISTICS {'─' * 21}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Views:{RESET} {BRIGHT_WHITE}{format_number(meta['view_count'])}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Likes:{RESET} {BRIGHT_WHITE}{format_number(meta['like_count'])}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Comments:{RESET} {BRIGHT_WHITE}{format_number(meta['comment_count'])}{RESET}")
        
        # Technical
        print(f"{NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}║{RESET} {NEON_CYAN}{'─' * 20} TECHNICAL {'─' * 22}{RESET}")
        
        resolution = f"{meta['width']}x{meta['height']}" if meta['width'] else 'N/A'
        print(f"{NEON_GREEN}║{RESET} {CYAN}Resolution:{RESET} {BRIGHT_WHITE}{resolution}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}FPS:{RESET} {BRIGHT_WHITE}{meta['fps']}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Video Codec:{RESET} {BRIGHT_WHITE}{meta['vcodec']}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Audio Codec:{RESET} {BRIGHT_WHITE}{meta['acodec']}{RESET}")
        
        if meta['filesize']:
            print(f"{NEON_GREEN}║{RESET} {CYAN}File Size:{RESET} {BRIGHT_WHITE}{format_size(meta['filesize'])}{RESET}")
        
        # Upload Info
        print(f"{NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}║{RESET} {NEON_CYAN}{'─' * 20} UPLOAD INFO {'─' * 20}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Upload Date:{RESET} {BRIGHT_WHITE}{meta['upload_date']}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Availability:{RESET} {BRIGHT_WHITE}{meta['availability']}{RESET}")
        
        # Tags
        if meta['tags']:
            print(f"{NEON_GREEN}║{RESET}")
            print(f"{NEON_GREEN}║{RESET} {NEON_CYAN}{'─' * 20} TAGS {'─' * 27}{RESET}")
            tags_str = ', '.join(meta['tags'][:10])
            print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{tags_str[:55]}{RESET}")
        
        print(f"{NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")
    
    def _export_metadata(self, meta: Dict):
        """Export metadata to file"""
        print(f"\n{NEON_CYAN}[?] Select Export Format:{RESET}\n")
        
        for key, label, _ in self.EXPORT_FORMATS:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")
        
        choice = get_input("Format", "1")
        
        format_choice = 'json'
        for key, label, value in self.EXPORT_FORMATS:
            if choice == key:
                format_choice = value
                break
        
        output_dir = self.create_output_dir('metadata')
        title = self.sanitize_filename(meta.get('title', 'metadata'))
        output_file = os.path.join(output_dir, f"{title}.{format_choice}")
        
        try:
            if format_choice == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(meta, f, indent=4, ensure_ascii=False, default=str)
                    
            elif format_choice == 'txt':
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"YouTube Video Metadata\n")
                    f.write(f"{'=' * 50}\n\n")
                    for key, value in meta.items():
                        f.write(f"{key.upper()}: {value}\n")
                        
            elif format_choice == 'csv':
                import csv
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Field', 'Value'])
                    for key, value in meta.items():
                        writer.writerow([key, str(value)])
            
            show_success_box("EXPORTED", f"Metadata saved to:\n{output_file}")
            
        except Exception as e:
            show_error_box("Error", f"Could not export: {str(e)}")
    
    def extract(self, url: str) -> Optional[Dict]:
        """Programmatic extraction"""
        video_id = get_video_id(url)
        if not video_id:
            return None
        return self._extract_metadata(url)


def run():
    """Run metadata extractor"""
    extractor = MetadataExtractor()
    extractor.run()


if __name__ == "__main__":
    run()
