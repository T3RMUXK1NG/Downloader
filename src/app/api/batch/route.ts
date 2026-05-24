import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { mkdir } from "fs/promises";
import path from "path";
import { v4 as uuidv4 } from "uuid";

const execAsync = promisify(exec);

const DOWNLOAD_DIR = path.join(process.cwd(), "downloads");

async function ensureDownloadDir() {
  try {
    await mkdir(DOWNLOAD_DIR, { recursive: true });
  } catch (error) {
    // Directory exists
  }
}

function escapeShellArg(arg: string): string {
  return `'${arg.replace(/'/g, "'\\''")}'`;
}

function sanitizeFilename(name: string): string {
  return name
    .replace(/[<>:"/\\|?*]/g, "_")
    .replace(/[\x00-\x1f]/g, "")
    .trim()
    .slice(0, 200) || "download";
}

interface BatchItem {
  id: string;
  url: string;
  type: "video" | "audio" | "thumbnail" | "subtitle";
  quality?: string;
  format?: string;
  status: "pending" | "downloading" | "complete" | "error";
  filename?: string;
  error?: string;
}

const batchJobs = new Map<string, BatchItem[]>();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { urls, type = "video", quality = "best", format = "mp4" } = body;

    if (!urls || !Array.isArray(urls) || urls.length === 0) {
      return NextResponse.json(
        { success: false, error: "URLs array is required" },
        { status: 400 }
      );
    }

    await ensureDownloadDir();

    const batchId = uuidv4();
    
    const items: BatchItem[] = urls.map((url: string) => ({
      id: uuidv4(),
      url,
      type,
      quality,
      format,
      status: "pending",
    }));

    batchJobs.set(batchId, items);

    processBatchDownloads(batchId, items, quality, format).catch(console.error);

    return NextResponse.json({
      success: true,
      batchId,
      totalItems: items.length,
      message: `Batch download started with ${items.length} items`,
    });
  } catch (error: any) {
    console.error("Batch download error:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Batch download failed" },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const batchId = searchParams.get("batchId");

  if (!batchId) {
    return NextResponse.json(
      { success: false, error: "batchId is required" },
      { status: 400 }
    );
  }

  const items = batchJobs.get(batchId);
  if (!items) {
    return NextResponse.json(
      { success: false, error: "Batch job not found" },
      { status: 404 }
    );
  }

  const completed = items.filter(i => i.status === "complete").length;
  const failed = items.filter(i => i.status === "error").length;
  const pending = items.filter(i => i.status === "pending" || i.status === "downloading").length;

  return NextResponse.json({
    success: true,
    batchId,
    items,
    progress: {
      total: items.length,
      completed,
      failed,
      pending,
      percentage: Math.round((completed + failed) / items.length * 100),
    },
  });
}

async function processBatchDownloads(
  batchId: string,
  items: BatchItem[],
  quality: string,
  format: string
) {
  for (const item of items) {
    try {
      item.status = "downloading";
      batchJobs.set(batchId, [...items]);

      let title = "download";
      try {
        const { stdout } = await execAsync(
          `yt-dlp --get-title --no-download "${item.url}"`,
          { timeout: 15000 }
        );
        title = stdout.trim();
      } catch (e) {
        // Use default title
      }

      const sanitizedTitle = sanitizeFilename(title);
      const extension = item.type === "audio" ? (item.format || "mp3") : 
                       item.type === "thumbnail" ? "jpg" :
                       item.type === "subtitle" ? "srt" : 
                       (item.format || "mp4");
      
      const filename = `${sanitizedTitle}.${extension}`;
      const outputPath = path.join(DOWNLOAD_DIR, filename);

      let command = "";
      const escapedUrl = escapeShellArg(item.url);
      const escapedOutput = escapeShellArg(outputPath);

      switch (item.type) {
        case "video":
          const height = (item.quality || quality).replace("p", "");
          const formatStr = item.quality === "best" 
            ? `bestvideo[ext=${item.format || format}]+bestaudio/best`
            : `bestvideo[height<=${height}][ext=${item.format || format}]+bestaudio/best[height<=${height}]`;
          command = `yt-dlp --no-playlist -f '${formatStr}' --merge-output-format ${item.format || format} -o ${escapedOutput} ${escapedUrl}`;
          break;
        case "audio":
          command = `yt-dlp --no-playlist -x --audio-format ${item.format || "mp3"} --audio-quality ${item.quality || "320"}K --embed-thumbnail --add-metadata -o ${escapedOutput} ${escapedUrl}`;
          break;
        case "thumbnail":
          command = `yt-dlp --no-playlist --write-thumbnail --skip-download -o ${escapedOutput} ${escapedUrl}`;
          break;
        case "subtitle":
          command = `yt-dlp --no-playlist --write-subs --sub-langs en --skip-download -o ${escapedOutput} ${escapedUrl}`;
          break;
        default:
          command = `yt-dlp --no-playlist -o ${escapedOutput} ${escapedUrl}`;
      }

      await execAsync(command, {
        timeout: 300000,
        maxBuffer: 1024 * 1024 * 50,
      });

      item.status = "complete";
      item.filename = filename;
    } catch (error: any) {
      item.status = "error";
      item.error = error.message || "Download failed";
    }

    batchJobs.set(batchId, [...items]);
  }
}
