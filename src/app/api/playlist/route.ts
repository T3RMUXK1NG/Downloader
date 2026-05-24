import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

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

    // Get playlist info using yt-dlp
    const { stdout } = await execAsync(
      `yt-dlp --flat-playlist --dump-json "${url}"`,
      { timeout: 60000, maxBuffer: 1024 * 1024 * 10 }
    );

    const entries = stdout
      .trim()
      .split("\n")
      .filter(line => line.trim())
      .map(line => {
        try {
          const data = JSON.parse(line);
          return {
            id: data.id || "",
            title: data.title || "Unknown",
            thumbnail: data.thumbnail || `https://i.ytimg.com/vi/${data.id}/hqdefault.jpg`,
            duration: data.duration ? formatDuration(data.duration) : "N/A",
            channel: data.channel || data.uploader || "Unknown",
            url: data.url || `https://www.youtube.com/watch?v=${data.id}`,
          };
        } catch {
          return null;
        }
      })
      .filter(entry => entry !== null);

    return NextResponse.json({
      success: true,
      playlist: entries,
      total: entries.length,
    });
  } catch (error: any) {
    console.error("Playlist fetch error:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to fetch playlist" },
      { status: 500 }
    );
  }
}

function formatDuration(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}
