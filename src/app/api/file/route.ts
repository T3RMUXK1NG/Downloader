import { NextRequest, NextResponse } from "next/server";
import { readFile, access } from "fs/promises";
import path from "path";

const DOWNLOAD_DIR = path.join(process.cwd(), "downloads");

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filename = searchParams.get("name");

    if (!filename) {
      return NextResponse.json(
        { error: "Filename is required" },
        { status: 400 }
      );
    }

    // Security: prevent directory traversal
    const safeName = path.basename(filename);
    const filePath = path.join(DOWNLOAD_DIR, safeName);

    // Check if file exists
    try {
      await access(filePath);
    } catch {
      return NextResponse.json(
        { error: "File not found" },
        { status: 404 }
      );
    }

    // Read file
    const fileBuffer = await readFile(filePath);

    // Determine content type
    const ext = path.extname(safeName).toLowerCase();
    const contentTypes: Record<string, string> = {
      ".mp4": "video/mp4",
      ".webm": "video/webm",
      ".mkv": "video/x-matroska",
      ".mp3": "audio/mpeg",
      ".m4a": "audio/mp4",
      ".flac": "audio/flac",
      ".opus": "audio/opus",
      ".wav": "audio/wav",
      ".jpg": "image/jpeg",
      ".jpeg": "image/jpeg",
      ".png": "image/png",
      ".srt": "application/x-subrip",
      ".vtt": "text/vtt",
    };

    const contentType = contentTypes[ext] || "application/octet-stream";

    return new NextResponse(fileBuffer, {
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": `attachment; filename="${safeName}"`,
        "Content-Length": fileBuffer.length.toString(),
      },
    });
  } catch (error: any) {
    console.error("File serve error:", error);
    return NextResponse.json(
      { error: "Failed to serve file" },
      { status: 500 }
    );
  }
}
