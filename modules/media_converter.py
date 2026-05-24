#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Module 9: Media Converter                   ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
import glob
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader_base import DownloaderBase
from utils.colors import *
from utils.banner import show_module_header, show_error_box, show_success_box
from utils.helpers import get_input, confirm, press_enter, format_size


class MediaConverter(DownloaderBase):
    """
    Media Converter Module
    - Convert video formats
    - Convert audio formats
    - Compress videos
    - Trim media
    - Extract audio from video
    """

    VIDEO_FORMATS = ['mp4', 'webm', 'mkv', 'avi', 'mov']
    AUDIO_FORMATS = ['mp3', 'm4a', 'aac', 'flac', 'ogg', 'wav']

    OPERATIONS = [
        ('1', 'Convert Video Format', 'video_convert'),
        ('2', 'Convert Audio Format', 'audio_convert'),
        ('3', 'Extract Audio from Video', 'extract_audio'),
        ('4', 'Compress Video', 'compress'),
        ('5', 'Trim Video/Audio', 'trim'),
        ('6', 'Merge Video + Audio', 'merge'),
    ]

    def __init__(self):
        super().__init__()
        self.name = "Media Converter"
        self.module_icon = "🔄"

    def run(self):
        """Run media converter module"""
        show_module_header(f"{self.module_icon} MEDIA CONVERTER", "▶")

        # Check FFmpeg
        if not self.is_ffmpeg_available():
            show_error_box(
                "FFmpeg Required",
                "FFmpeg is not installed.\n"
                "Install with:\n"
                "  Ubuntu/Debian: sudo apt install ffmpeg\n"
                "  Termux: pkg install ffmpeg\n"
                "  Windows: Download from ffmpeg.org"
            )
            return

        # Select operation
        print(f"{NEON_CYAN}[?] Select Operation:{RESET}\n")
        for key, label, _ in self.OPERATIONS:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")

        choice = get_input("Operation", "1")

        operation = None
        for key, label, value in self.OPERATIONS:
            if choice == key:
                operation = value
                break

        if not operation:
            show_error_box("Invalid", "Invalid operation")
            return

        # Execute operation
        self._execute_operation(operation)

    def _execute_operation(self, operation: str):
        """Execute selected operation"""
        if operation == 'video_convert':
            self._convert_video()
        elif operation == 'audio_convert':
            self._convert_audio()
        elif operation == 'extract_audio':
            self._extract_audio()
        elif operation == 'compress':
            self._compress_video()
        elif operation == 'trim':
            self._trim_media()
        elif operation == 'merge':
            self._merge_media()

    def _get_input_file(self, media_type: str = "media") -> Optional[str]:
        """Get input file from user"""
        print(f"\n{NEON_CYAN}[?] Enter input file path:{RESET}")
        print(f"  {DIM}Or press Enter to browse output folder{RESET}")

        filepath = get_input("File")

        if not filepath:
            # Browse output folder
            output_dir = self.create_output_dir()
            files = []

            for ext in self.VIDEO_FORMATS + self.AUDIO_FORMATS:
                files.extend(glob.glob(os.path.join(output_dir, '**', f'*.{ext}'), recursive=True))

            if not files:
                show_error_box("No Files", "No media files found in output folder")
                return None

            print(f"\n{NEON_CYAN}[?] Select file:{RESET}\n")
            for i, f in enumerate(files[:10], 1):
                print(f"  {NEON_GREEN}[{i}]{RESET} {os.path.basename(f)}")

            selection = get_input("Select")
            try:
                index = int(selection) - 1
                if 0 <= index < len(files):
                    return files[index]
            except Exception:
                pass

            return None

        # Check if file exists
        if os.path.exists(filepath):
            return filepath

        show_error_box("File Not Found", f"File not found: {filepath}")
        return None

    def _convert_video(self):
        """Convert video format"""
        input_file = self._get_input_file("video")
        if not input_file:
            return

        # Get output format
        print(f"\n{NEON_CYAN}[?] Select output format:{RESET}\n")
        for i, fmt in enumerate(self.VIDEO_FORMATS, 1):
            print(f"  {NEON_GREEN}[{i}]{RESET} {fmt.upper()}")

        choice = get_input("Format", "1")
        try:
            output_format = self.VIDEO_FORMATS[int(choice) - 1]
        except Exception:
            output_format = 'mp4'

        # Output file
        base = os.path.splitext(input_file)[0]
        output_file = f"{base}_converted.{output_format}"

        print(f"\n{NEON_GREEN}[+] Converting video...{RESET}")

        if self._run_ffmpeg_convert(input_file, output_file, output_format):
            show_success_box("SUCCESS", f"Converted to:\n{output_file}")
        else:
            show_error_box("Error", "Conversion failed")

        press_enter()

    def _convert_audio(self):
        """Convert audio format"""
        input_file = self._get_input_file("audio")
        if not input_file:
            return

        print(f"\n{NEON_CYAN}[?] Select output format:{RESET}\n")
        for i, fmt in enumerate(self.AUDIO_FORMATS, 1):
            print(f"  {NEON_GREEN}[{i}]{RESET} {fmt.upper()}")

        choice = get_input("Format", "1")
        try:
            output_format = self.AUDIO_FORMATS[int(choice) - 1]
        except Exception:
            output_format = 'mp3'

        base = os.path.splitext(input_file)[0]
        output_file = f"{base}.{output_format}"

        print(f"\n{NEON_GREEN}[+] Converting audio...{RESET}")

        cmd = [self.ffmpeg_path, '-y', '-i', input_file]

        if output_format == 'mp3':
            cmd.extend(['-acodec', 'libmp3lame', '-b:a', '320k'])
        elif output_format == 'aac':
            cmd.extend(['-acodec', 'aac', '-b:a', '256k'])
        elif output_format == 'flac':
            cmd.extend(['-acodec', 'flac'])

        cmd.append(output_file)

        if self._run_ffmpeg(cmd):
            show_success_box("SUCCESS", f"Converted to:\n{output_file}")
        else:
            show_error_box("Error", "Conversion failed")

        press_enter()

    def _extract_audio(self):
        """Extract audio from video"""
        input_file = self._get_input_file("video")
        if not input_file:
            return

        print(f"\n{NEON_CYAN}[?] Select audio format:{RESET}\n")
        for i, fmt in enumerate(['mp3', 'm4a', 'aac', 'flac'], 1):
            print(f"  {NEON_GREEN}[{i}]{RESET} {fmt.upper()}")

        choice = get_input("Format", "1")
        audio_format = ['mp3', 'm4a', 'aac', 'flac'][int(choice) - 1] if choice.isdigit() else 'mp3'

        base = os.path.splitext(input_file)[0]
        output_file = f"{base}.{audio_format}"

        print(f"\n{NEON_GREEN}[+] Extracting audio...{RESET}")

        cmd = [self.ffmpeg_path, '-y', '-i', input_file, '-vn']

        if audio_format == 'mp3':
            cmd.extend(['-acodec', 'libmp3lame', '-b:a', '320k'])
        elif audio_format == 'm4a':
            cmd.extend(['-acodec', 'aac', '-b:a', '256k'])
        elif audio_format == 'flac':
            cmd.extend(['-acodec', 'flac'])

        cmd.append(output_file)

        if self._run_ffmpeg(cmd):
            show_success_box("SUCCESS", f"Audio extracted to:\n{output_file}")
        else:
            show_error_box("Error", "Extraction failed")

        press_enter()

    def _compress_video(self):
        """Compress video"""
        input_file = self._get_input_file("video")
        if not input_file:
            return

        print(f"\n{NEON_CYAN}[?] Compression level:{RESET}\n")
        print(f"  {NEON_GREEN}[1]{RESET} Low (Better Quality)")
        print(f"  {NEON_GREEN}[2]{RESET} Medium (Balanced)")
        print(f"  {NEON_GREEN}[3]{RESET} High (Smaller Size)")

        choice = get_input("Level", "2")

        crf = {'1': '23', '2': '28', '3': '33'}.get(choice, '28')

        base = os.path.splitext(input_file)[0]
        output_file = f"{base}_compressed.mp4"

        # Get original size
        original_size = os.path.getsize(input_file)

        print(f"\n{NEON_GREEN}[+] Compressing video...{RESET}")
        print(f"{NEON_CYAN}[→] Original size: {format_size(original_size)}{RESET}")

        cmd = [
            self.ffmpeg_path, '-y', '-i', input_file,
            '-c:v', 'libx264', '-crf', crf,
            '-preset', 'medium',
            '-c:a', 'aac', '-b:a', '128k',
            output_file
        ]

        if self._run_ffmpeg(cmd):
            new_size = os.path.getsize(output_file)
            saved = original_size - new_size
            percent = (saved / original_size * 100) if original_size > 0 else 0

            show_success_box(
                "SUCCESS",
                f"Compressed: {format_size(new_size)}\n"
                f"Saved: {format_size(saved)} ({percent:.1f}%)\n"
                f"Output: {output_file}"
            )
        else:
            show_error_box("Error", "Compression failed")

        press_enter()

    def _trim_media(self):
        """Trim video or audio"""
        input_file = self._get_input_file("media")
        if not input_file:
            return

        print(f"\n{NEON_CYAN}[?] Enter start time (format: MM:SS or seconds):{RESET}")
        start_time = get_input("Start", "0")

        print(f"\n{NEON_CYAN}[?] Enter end time (format: MM:SS or seconds):{RESET}")
        end_time = get_input("End", "60")

        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_trimmed{ext}"

        print(f"\n{NEON_GREEN}[+] Trimming media...{RESET}")

        cmd = [
            self.ffmpeg_path, '-y', '-i', input_file,
            '-ss', start_time,
            '-to', end_time,
            '-c', 'copy',
            output_file
        ]

        if self._run_ffmpeg(cmd):
            show_success_box("SUCCESS", f"Trimmed media saved to:\n{output_file}")
        else:
            show_error_box("Error", "Trimming failed")

        press_enter()

    def _merge_media(self):
        """Merge video and audio"""
        print(f"\n{NEON_CYAN}[?] Select video file:{RESET}")
        video_file = self._get_input_file("video")

        if not video_file:
            return

        print(f"\n{NEON_CYAN}[?] Select audio file:{RESET}")
        audio_file = self._get_input_file("audio")

        if not audio_file:
            return

        base = os.path.splitext(video_file)[0]
        output_file = f"{base}_merged.mp4"

        print(f"\n{NEON_GREEN}[+] Merging video and audio...{RESET}")

        cmd = [
            self.ffmpeg_path, '-y',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            output_file
        ]

        if self._run_ffmpeg(cmd):
            show_success_box("SUCCESS", f"Merged media saved to:\n{output_file}")
        else:
            show_error_box("Error", "Merge failed")

        press_enter()

    def _run_ffmpeg_convert(self, input_file: str, output_file: str, output_format: str) -> bool:
        """Run FFmpeg conversion"""
        cmd = [self.ffmpeg_path, '-y', '-i', input_file]

        if output_format == 'mp4':
            cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])
        elif output_format == 'webm':
            cmd.extend(['-c:v', 'libvpx-vp9', '-c:a', 'libopus'])
        elif output_format == 'mkv':
            cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])

        cmd.append(output_file)
        return self._run_ffmpeg(cmd)

    def _run_ffmpeg(self, cmd: list) -> bool:
        """Execute FFmpeg command"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=600
            )
            return result.returncode == 0
        except Exception:
            return False

    def convert(self, input_file: str, output_file: str) -> Tuple[bool, str]:
        """Programmatic conversion"""
        if not self.is_ffmpeg_available():
            return False, "FFmpeg not available"

        output_format = os.path.splitext(output_file)[1][1:]

        if self._run_ffmpeg_convert(input_file, output_file, output_format):
            return True, output_file

        return False, "Conversion failed"


def run():
    """Run media converter"""
    converter = MediaConverter()
    converter.run()


if __name__ == "__main__":
    run()
