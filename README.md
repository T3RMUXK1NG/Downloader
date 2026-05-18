# 🔥 RS DOWNLOADER TOOLKIT 🔥

<div align="center">

![RS Downloader Toolkit](https://img.shields.io/badge/RS%20DOWNLOADER-TOOLKIT-brightgreen?style=for-the-badge&logo=youtube&logoColor=white)
![Version](https://img.shields.io/badge/VERSION-1.0.0%20GOD%20MODE-blue?style=for-the-badge)
![Author](https://img.shields.io/badge/AUTHOR-RS%20(T3rmuxk1ng)-red?style=for-the-badge)
![Python](https://img.shields.io/badge/PYTHON-3.6+-yellow?style=for-the-badge&logo=python&logoColor=white)

**LEGENDARY YouTube Downloader Toolkit with Hacker Style Terminal UI**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Modules](#-modules)

</div>

---

## 📌 About

**RS Downloader Toolkit** is a powerful, modular YouTube downloader with a full hacker-style terminal UI. Built from scratch in pure Python with FFmpeg integration for complete media conversion support.

### 🎯 Key Highlights

- 🖥️ **Hacker Terminal UI** - Neon green/cyan theme with Matrix-style aesthetics
- 📦 **Modular Architecture** - 9 independent modules for different tasks
- 📱 **Termux Compatible** - Works on Android via Termux
- 🔄 **FFmpeg Integration** - Full conversion and processing support
- ⚡ **Pure Python** - Built from scratch, no heavy dependencies

---

## ✨ Features

| # | Module | Description |
|---|--------|-------------|
| 1 | 🎬 **Video Downloader** | Download videos in 4K, 1080p, 720p, etc. (MP4, WEBM, MKV) |
| 2 | 🎵 **Audio Downloader** | Extract audio in MP3, M4A, FLAC, AAC, OPUS |
| 3 | 📁 **Playlist Downloader** | Download entire playlists with parallel support |
| 4 | 🖼️ **Thumbnail Grabber** | Download video thumbnails in max quality |
| 5 | 📊 **Metadata Extractor** | Extract video info, export to JSON/TXT/CSV |
| 6 | 📝 **Subtitle Downloader** | Download subtitles in SRT, VTT, TXT formats |
| 7 | 📦 **Batch Downloader** | Download multiple URLs at once |
| 8 | 🔍 **Search & Download** | Search YouTube and download directly |
| 9 | 🔄 **Media Converter** | Convert, compress, trim, and merge media |

---

## 🚀 Installation

### Prerequisites

- Python 3.6+
- FFmpeg (for media conversion)
- Internet connection

### Quick Install

```bash
# Clone the repository
git clone https://github.com/T3RMUXK1NG/Downloader.git
cd Downloader

# Install dependencies
pip install -r requirements.txt

# Run the toolkit
python rs_toolkit.py
```

### Termux (Android) Setup

```bash
# Update packages
pkg update && pkg upgrade

# Install Python and FFmpeg
pkg install python ffmpeg

# Clone and run
git clone https://github.com/T3RMUXK1NG/Downloader.git
cd Downloader
pip install -r requirements.txt
python rs_toolkit.py
```

### FFmpeg Installation

| Platform | Command |
|----------|---------|
| **Termux** | `pkg install ffmpeg` |
| **Ubuntu/Debian** | `sudo apt install ffmpeg` |
| **macOS** | `brew install ffmpeg` |
| **Windows** | Download from [ffmpeg.org](https://ffmpeg.org) |

---

## 📖 Usage

### Running the Toolkit

```bash
python rs_toolkit.py
```

### Video Download Example

1. Select `[1] Video Downloader`
2. Paste YouTube URL
3. Select quality (4K, 1080p, 720p, etc.)
4. Select format (MP4, WEBM, MKV)
5. Confirm download

### Audio Extraction Example

1. Select `[2] Audio Downloader`
2. Paste YouTube URL
3. Select format (MP3, M4A, FLAC)
4. Select quality (64-320 kbps)
5. Choose to embed thumbnail/metadata

---

## 📁 Project Structure

```
Downloader/
├── rs_toolkit.py              # Main Entry Point
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
│
├── core/                      # Core Infrastructure
│   ├── downloader_base.py     # Base class for all modules
│   ├── network.py             # Network handler
│   ├── config.py              # Configuration manager
│   └── logger.py              # Logging system
│
├── modules/                   # Feature Modules
│   ├── video_downloader.py
│   ├── audio_downloader.py
│   ├── playlist_downloader.py
│   ├── thumbnail_grabber.py
│   ├── metadata_extractor.py
│   ├── subtitle_downloader.py
│   ├── batch_downloader.py
│   ├── search_download.py
│   └── media_converter.py
│
└── utils/                     # Utilities
    ├── colors.py
    ├── banner.py
    ├── helpers.py
    ├── progress.py
    └── validator.py
```

---

## 👤 Author

<div align="center">

**RS (RAJSARASWATI JATAV)**

[![YouTube](https://img.shields.io/badge/YouTube-T3rmuxk1ng-red?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/@T3rmuxk1ng)
[![GitHub](https://img.shields.io/badge/GitHub-T3RMUXK1NG-black?style=for-the-badge&logo=github&logoColor=white)](https://github.com/T3RMUXK1NG)

🔥 **LEGENDARY EXPERT - GOD MODE NEXUS** 🔥

</div>

---

<div align="center">

**Made with ❤️ by RS (T3rmuxk1ng)**

</div>
