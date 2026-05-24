import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { writeFile, mkdir } from "fs/promises";
import path from "path";

const execAsync = promisify(exec);

// Output directory for downloads
const DOWNLOAD_DIR = path.join(process.cwd(), "downloads");

// Ensure download directory exists
async function ensureDownloadDir() {
  try {
    await mkdir(DOWNLOAD_DIR, { recursive: true });
  } catch (error) {
    // Directory exists
  }
}

// Extract video ID from YouTube URL
function extractVideoId(url: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/live\/([a-zA-Z0-9_-]{11})/,
  ];

  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }
  return null;
}

// Get video info using yt-dlp
async function getVideoInfo(url: string): Promise<any> {
  try {
    const { stdout } = await execAsync(
      `yt-dlp --dump-json --no-download "${url}"`,
      { timeout: 30000 }
    );
    return JSON.parse(stdout);
  } catch (error) {
    throw new Error("Failed to fetch video info");
  }
}

// Sanitize filename
function sanitizeFilename(name: string): string {
  return name
    .replace(/[<>:"/\\|?*]/g, "_")
    .replace(/[\x00-\x1f]/g, "")
    .trim()
    .slice(0, 200) || "download";
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { url } = body;

    if (!url) {
      return NextResponse.json(
        { success: false, error: "URL is required" },
        { status: 400 }
      );
    }

    await ensureDownloadDir();

    // Get video info
    const info = await getVideoInfo(url);

    const videoId = info.id || extractVideoId(url) || "unknown";
    const title = info.title || `video_${videoId}`;
    const duration = info.duration || 0;
    const thumbnail =
      info.thumbnail ||
      info.thumbnails?.[0]?.url ||
      `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
    const channel = info.uploader || info.channel || "Unknown";
    const viewCount = info.view_count || 0;
    const description = info.description || "";

    // Format duration
    const formatDuration = (seconds: number): string => {
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      const s = Math.floor(seconds % 60);
      if (h > 0) return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
      return `${m}:${s.toString().padStart(2, "0")}`;
    };

    // Format view count
    const formatViews = (views: number): string => {
      if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`;
      if (views >= 1000) return `${(views / 1000).toFixed(1)}K`;
      return views.toString();
    };

    return NextResponse.json({
      success: true,
      info: {
        id: videoId,
        title,
        thumbnail,
        duration: formatDuration(duration),
        channel,
        viewCount: formatViews(viewCount),
        description: description.slice(0, 500),
      },
    });
  } catch (error: any) {
    console.error("Info error:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to get video info" },
      { status: 500 }
    );
  }
}
