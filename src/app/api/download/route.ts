import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { mkdir, access } from "fs/promises";
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
async function getVideoTitle(url: string): Promise<string> {
  try {
    const { stdout } = await execAsync(
      `yt-dlp --get-title --no-download "${url}"`,
      { timeout: 15000 }
    );
    return stdout.trim();
  } catch (error) {
    return "download";
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

// Escape shell argument
function escapeShellArg(arg: string): string {
  return `'${arg.replace(/'/g, "'\\''")}'`;
}

// Build yt-dlp command based on download type
function buildCommand(
  url: string,
  type: string,
  options: Record<string, string | boolean>,
  outputPath: string
): string {
  const escapedUrl = escapeShellArg(url);
  const escapedOutput = escapeShellArg(outputPath);

  switch (type) {
    case "video": {
      const quality = (options.quality as string) || "best";
      const format = (options.format as string) || "mp4";
      
      let formatStr: string;
      if (quality === "best") {
        formatStr = `bestvideo[ext=${format}]+bestaudio/best[ext=${format}]/best`;
      } else {
        const height = quality.replace("p", "");
        formatStr = `bestvideo[height<=${height}][ext=${format}]+bestaudio/best[height<=${height}]/best`;
      }

      // Use single quotes to prevent bash interpretation
      return `yt-dlp --no-playlist -f '${formatStr}' --merge-output-format ${format} -o ${escapedOutput} ${escapedUrl}`;
    }

    case "audio": {
      const quality = (options.quality as string) || "320";
      const format = (options.format as string) || "mp3";
      const embedThumb = options.embedThumbnail ? "--embed-thumbnail" : "";

      return `yt-dlp --no-playlist -x --audio-format ${format} --audio-quality ${quality}K ${embedThumb} --add-metadata -o ${escapedOutput} ${escapedUrl}`;
    }

    case "thumbnail": {
      return `yt-dlp --no-playlist --write-thumbnail --skip-download -o ${escapedOutput} ${escapedUrl}`;
    }

    case "subtitle": {
      const lang = (options.language as string) || "en";
      return `yt-dlp --no-playlist --write-subs --sub-langs ${lang} --skip-download -o ${escapedOutput} ${escapedUrl}`;
    }

    default:
      return `yt-dlp --no-playlist -o ${escapedOutput} ${escapedUrl}`;
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { url, type = "video", quality, format, embedThumbnail, language } = body;

    if (!url) {
      return NextResponse.json(
        { success: false, error: "URL is required" },
        { status: 400 }
      );
    }

    await ensureDownloadDir();

    // Get video title for filename
    const title = await getVideoTitle(url);
    const sanitizedTitle = sanitizeFilename(title);
    const videoId = extractVideoId(url) || Date.now().toString();

    // Determine file extension
    let extension = "mp4";
    if (type === "audio") {
      extension = format || "mp3";
    } else if (type === "thumbnail") {
      extension = "jpg";
    } else if (type === "subtitle") {
      extension = "srt";
    } else {
      extension = format || "mp4";
    }

    const filename = `${sanitizedTitle}.${extension}`;
    const outputPath = path.join(DOWNLOAD_DIR, filename);

    // Build and execute command
    const options: Record<string, string | boolean> = {};
    if (quality) options.quality = quality;
    if (format) options.format = format;
    if (embedThumbnail !== undefined) options.embedThumbnail = embedThumbnail;
    if (language) options.language = language;

    const command = buildCommand(url, type, options, outputPath);
    
    console.log(`Executing: ${command}`);

    const { stdout, stderr } = await execAsync(command, {
      timeout: 300000, // 5 minutes timeout
      maxBuffer: 1024 * 1024 * 50, // 50MB buffer
    });

    // Check if file exists
    try {
      await access(outputPath);
    } catch {
      // Try to find the actual file (yt-dlp might have changed the name)
      const { stdout: lsOutput } = await execAsync(
        `ls -t "${DOWNLOAD_DIR}" | head -1`
      );
      if (lsOutput.trim()) {
        return NextResponse.json({
          success: true,
          filename: lsOutput.trim(),
          message: "Download completed",
        });
      }
      
      return NextResponse.json(
        { success: false, error: "Download failed - file not created" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      filename,
      downloadUrl: `/api/file?name=${encodeURIComponent(filename)}`,
      message: "Download completed successfully",
    });
  } catch (error: any) {
    console.error("Download error:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Download failed" },
      { status: 500 }
    );
  }
}
