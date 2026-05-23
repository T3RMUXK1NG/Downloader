# 🔥 RS DOWNLOADER TOOLKIT v2.0 - GOD MODE NEXUS 🔥

<div align="center">

![RS Downloader Toolkit](https://img.shields.io/badge/RS%20DOWNLOADER-TOOLKIT-brightgreen?style=for-the-badge&logo=youtube&logoColor=white)
![Version](https://img.shields.io/badge/VERSION-2.0.0%20GOD%20MODE%20NEXUS-blue?style=for-the-badge)
![Author](https://img.shields.io/badge/AUTHOR-RS%20(T3rmuxk1ng)-red?style=for-the-badge)
![Python](https://img.shields.io/badge/PYTHON-3.7+-yellow?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/LICENSE-MIT-green?style=for-the-badge)

**🔱 LEGENDARY YouTube Downloader Toolkit with Hacker Style Terminal UI 🔱**

**Full-Stack Next.js Web Interface | Multi-Platform Support | FFmpeg Integration**

[Features](#-features) • [Installation](#-installation) • [Web Interface](#-web-interface) • [CLI Usage](#-cli-usage) • [API](#-api-reference)

</div>

---

## 📌 About

**RS Downloader Toolkit v2.0 GOD MODE NEXUS** is a powerful, modular YouTube and multi-platform downloader with both a full hacker-style terminal UI and a modern web interface. Built from scratch in pure Python with FFmpeg integration for complete media conversion support.

### 🎯 Key Highlights

- 🖥️ **Hacker Terminal UI** - Neon green/cyan theme with Matrix-style aesthetics
- 🌐 **Full-Stack Web Interface** - Next.js 16 with beautiful hacker-style UI
- 📦 **Modular Architecture** - 9 independent modules for different tasks
- 📱 **Termux Compatible** - Works on Android via Termux
- 🔄 **FFmpeg Integration** - Full conversion and processing support
- ⚡ **Pure Python** - Built from scratch, no heavy dependencies
- 🚀 **Multi-Platform** - YouTube, Twitch, Twitter, Instagram, TikTok, +100 more

---

## ✨ Features

| # | Module | CLI | Web | Description |
|---|--------|-----|-----|-------------|
| 1 | 🎬 **Video Downloader** | ✅ | ✅ | Download videos in 4K, 1080p, 720p, etc. (MP4, WEBM, MKV) |
| 2 | 🎵 **Audio Downloader** | ✅ | ✅ | Extract audio in MP3, M4A, FLAC, AAC, OPUS |
| 3 | 📁 **Playlist Downloader** | ✅ | ✅ | Download entire playlists with parallel support |
| 4 | 🖼️ **Thumbnail Grabber** | ✅ | ✅ | Download video thumbnails in max quality |
| 5 | 📊 **Metadata Extractor** | ✅ | ✅ | Extract video info, export to JSON/TXT/CSV |
| 6 | 📝 **Subtitle Downloader** | ✅ | ✅ | Download subtitles in SRT, VTT, TXT formats |
| 7 | 📦 **Batch Downloader** | ✅ | ✅ | Download multiple URLs at once |
| 8 | 🔍 **Search & Download** | ✅ | ✅ | Search YouTube and download directly |
| 9 | 🔄 **Media Converter** | ✅ | ✅ | Convert, compress, trim, and merge media |

---

## 🚀 Installation

### Prerequisites

- Python 3.7+
- FFmpeg (for media conversion)
- Node.js 18+ (for web interface)
- Internet connection

### Quick Install (CLI)

```bash
# Clone the repository
git clone https://github.com/T3RMUXK1NG/Downloader.git
cd Downloader

# Install dependencies
pip install -r requirements.txt

# Run the toolkit
python rs_toolkit.py
```

### Web Interface Setup

```bash
# Clone the repository
git clone https://github.com/T3RMUXK1NG/Downloader.git
cd Downloader

# Install Node.js dependencies
npm install

# Run development server
npm run dev

# Or build for production
npm run build
npm start
```

### Termux (Android) Setup

```bash
# Update packages
pkg update && pkg upgrade

# Install Python and FFmpeg
pkg install python ffmpeg nodejs

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

## 🌐 Web Interface

The v2.0 GOD MODE NEXUS includes a full-stack Next.js web application with:

- **Beautiful Hacker UI** - Dark theme with neon green accents
- **Real-time Progress** - Live download progress tracking
- **Multi-Platform** - Responsive design for all devices
- **Download History** - Track your downloads
- **API Endpoints** - Full REST API for integration

### Web Features

- 🎬 Video download with quality selection
- 🎵 Audio extraction with format options
- 🖼️ Thumbnail download
- 📝 Subtitle download with language selection
- 📊 Video information preview

---

## 📖 CLI Usage

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

## 🔧 API Reference

### Get Video Info

```http
POST /api/info
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=..."
}
```

**Response:**
```json
{
  "success": true,
  "info": {
    "id": "video_id",
    "title": "Video Title",
    "thumbnail": "https://...",
    "duration": "10:30",
    "channel": "Channel Name",
    "viewCount": "1.2M"
  }
}
```

### Start Download

```http
POST /api/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=...",
  "type": "video",
  "quality": "1080p",
  "format": "mp4"
}
```

**Response:**
```json
{
  "success": true,
  "filename": "video_title.mp4",
  "downloadUrl": "/api/file?name=video_title.mp4"
}
```

---

## 📁 Project Structure

```
Downloader/
├── rs_toolkit.py              # Main Entry Point (CLI)
├── requirements.txt           # Python Dependencies
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
├── utils/                     # Utilities
│   ├── colors.py
│   ├── banner.py
│   ├── helpers.py
│   ├── progress.py
│   └── validator.py
│
├── src/                       # Next.js Web App
│   ├── app/
│   │   ├── page.tsx          # Main Web UI
│   │   ├── api/              # API Routes
│   │   └── globals.css       # Hacker Styling
│   └── components/            # UI Components
│
├── .github/                   # GitHub Actions
│   └── workflows/
│       ├── ci-cd.yml         # CI/CD Pipeline
│       └── publish.yml       # Release Publishing
│
└── Dockerfile                 # Docker Support
```

---

## 🔱 GOD MODE NEXUS Features

### v2.0 New Features

- 🌐 **Full-Stack Web Interface** - Next.js 16 application
- 🔗 **REST API** - Complete API for integration
- 🐳 **Docker Support** - Containerized deployment
- 🚀 **GitHub Actions** - Automated CI/CD pipeline
- 📊 **Real-time Progress** - Live download tracking
- 🔐 **Enhanced Security** - Input validation & sanitization
- 📱 **Better Termux Support** - Optimized for mobile
- 🎨 **New Theme** - GOD MODE NEXUS color scheme

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

<div align="center">

**RS (RAJSARASWATI JATAV)**

[![YouTube](https://img.shields.io/badge/YouTube-T3rmuxk1ng-red?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/@T3rmuxk1ng)
[![GitHub](https://img.shields.io/badge/GitHub-T3RMUXK1NG-black?style=for-the-badge&logo=github&logoColor=white)](https://github.com/T3RMUXK1NG)

🔱 **LEGENDARY EXPERT - GOD MODE NEXUS** 🔥

</div>

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Made with ❤️ by RS (T3rmuxk1ng)**

🔱 **GOD MODE NEXUS v2.0 - POWER UNLEASHED** 🔱

</div>
