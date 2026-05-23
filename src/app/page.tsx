"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Download, 
  Music, 
  Video, 
  FileVideo, 
  Image, 
  FileText, 
  Subtitles, 
  Search, 
  Settings, 
  Github, 
  Youtube, 
  Zap, 
  Shield, 
  Terminal,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Trash2,
  ExternalLink,
  Copy,
  RefreshCw
} from "lucide-react";
import { toast } from "sonner";

interface VideoInfo {
  id: string;
  title: string;
  thumbnail: string;
  duration: string;
  channel: string;
  viewCount: string;
  description: string;
}

interface DownloadProgress {
  status: string;
  progress: number;
  speed: string;
  eta: string;
  filename: string;
}

const API_BASE = "/api";

export default function RSDownloaderApp() {
  const [url, setUrl] = useState("");
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<DownloadProgress | null>(null);
  const [downloadHistory, setDownloadHistory] = useState<Array<{ url: string; title: string; timestamp: Date }>>([]);
  
  // Video settings
  const [videoQuality, setVideoQuality] = useState("1080p");
  const [videoFormat, setVideoFormat] = useState("mp4");
  
  // Audio settings
  const [audioQuality, setAudioQuality] = useState("320");
  const [audioFormat, setAudioFormat] = useState("mp3");
  const [embedThumbnail, setEmbedThumbnail] = useState(true);
  
  // Subtitle settings
  const [subtitleLang, setSubtitleLang] = useState("en");

  const videoQualities = [
    { value: "4k", label: "4K Ultra HD (2160p)" },
    { value: "1440p", label: "2K QHD (1440p)" },
    { value: "1080p", label: "Full HD (1080p)" },
    { value: "720p", label: "HD (720p)" },
    { value: "480p", label: "SD (480p)" },
    { value: "360p", label: "Low (360p)" },
    { value: "best", label: "Best Available" },
  ];

  const videoFormats = [
    { value: "mp4", label: "MP4 (Recommended)" },
    { value: "webm", label: "WebM" },
    { value: "mkv", label: "MKV" },
  ];

  const audioQualities = [
    { value: "320", label: "320 kbps (Best)" },
    { value: "256", label: "256 kbps (High)" },
    { value: "192", label: "192 kbps (Good)" },
    { value: "128", label: "128 kbps (Normal)" },
    { value: "96", label: "96 kbps (Low)" },
  ];

  const audioFormats = [
    { value: "mp3", label: "MP3 (Universal)" },
    { value: "m4a", label: "M4A (Best Quality)" },
    { value: "flac", label: "FLAC (Lossless)" },
    { value: "opus", label: "Opus (Efficient)" },
    { value: "wav", label: "WAV (Uncompressed)" },
  ];

  const fetchVideoInfo = async () => {
    if (!url) {
      toast.error("Please enter a URL");
      return;
    }

    setLoading(true);
    setVideoInfo(null);

    try {
      const response = await fetch(`${API_BASE}/info`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (data.success) {
        setVideoInfo(data.info);
        toast.success("Video information fetched!");
      } else {
        toast.error(data.error || "Failed to fetch video info");
      }
    } catch (error) {
      toast.error("Failed to connect to server");
    } finally {
      setLoading(false);
    }
  };

  const startDownload = async (type: "video" | "audio" | "thumbnail" | "subtitle") => {
    if (!url) {
      toast.error("Please enter a URL");
      return;
    }

    setDownloading(true);
    setDownloadProgress({ status: "starting", progress: 0, speed: "", eta: "", filename: "" });

    try {
      const body: Record<string, unknown> = { url, type };

      if (type === "video") {
        body.quality = videoQuality;
        body.format = videoFormat;
      } else if (type === "audio") {
        body.quality = audioQuality;
        body.format = audioFormat;
        body.embedThumbnail = embedThumbnail;
      } else if (type === "subtitle") {
        body.language = subtitleLang;
      }

      const response = await fetch(`${API_BASE}/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (data.success) {
        setDownloadProgress({
          status: "complete",
          progress: 100,
          speed: "",
          eta: "",
          filename: data.filename || "download",
        });

        // Add to history
        setDownloadHistory(prev => [
          { url, title: videoInfo?.title || "Unknown", timestamp: new Date() },
          ...prev.slice(0, 19),
        ]);

        toast.success("Download complete!");

        // Trigger file download
        if (data.downloadUrl) {
          window.open(data.downloadUrl, "_blank");
        }
      } else {
        setDownloadProgress({
          status: "error",
          progress: 0,
          speed: "",
          eta: "",
          filename: data.error || "Download failed",
        });
        toast.error(data.error || "Download failed");
      }
    } catch (error) {
      toast.error("Failed to start download");
      setDownloadProgress({
        status: "error",
        progress: 0,
        speed: "",
        eta: "",
        filename: "Connection error",
      });
    } finally {
      setDownloading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  const formatDuration = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="min-h-screen bg-black text-green-400">
      {/* Matrix-style background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-5">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_#00ff00_1px,_transparent_1px)] bg-[length:20px_20px]" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-green-500/30 bg-black/90 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/20 border border-green-500/50">
                <Terminal className="h-6 w-6 text-green-400" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider text-green-400">
                  RS DOWNLOADER TOOLKIT
                </h1>
                <p className="text-xs text-green-600">v2.0 GOD MODE NEXUS</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Badge variant="outline" className="border-green-500/50 text-green-400">
                <Zap className="h-3 w-3 mr-1" />
                ACTIVE
              </Badge>
              <a
                href="https://github.com/T3RMUXK1NG/Downloader"
                target="_blank"
                rel="noopener noreferrer"
                className="text-green-400 hover:text-green-300 transition-colors"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="https://youtube.com/@T3rmuxk1ng"
                target="_blank"
                rel="noopener noreferrer"
                className="text-green-400 hover:text-green-300 transition-colors"
              >
                <Youtube className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Left Panel - URL Input & Video Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* URL Input Card */}
            <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-green-400 flex items-center gap-2">
                  <Download className="h-5 w-5" />
                  DOWNLOAD CENTER
                </CardTitle>
                <CardDescription className="text-green-600">
                  Enter YouTube, Twitch, Twitter, or supported platform URL
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-3">
                  <Input
                    type="url"
                    placeholder="https://www.youtube.com/watch?v=..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="flex-1 bg-black/50 border-green-500/30 text-green-400 placeholder:text-green-700 focus:border-green-500 focus:ring-green-500/20"
                  />
                  <Button
                    onClick={fetchVideoInfo}
                    disabled={loading}
                    className="bg-green-500 hover:bg-green-600 text-black font-semibold"
                  >
                    {loading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Video Info Card */}
            {videoInfo && (
              <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                <CardContent className="p-0">
                  <div className="flex flex-col md:flex-row">
                    <div className="relative aspect-video md:w-80 shrink-0">
                      <img alt="Video thumbnail"
                        src={videoInfo.thumbnail}
                        alt={videoInfo.title}
                        className="w-full h-full object-cover rounded-t-lg md:rounded-l-lg md:rounded-tr-none"
                      />
                      <Badge className="absolute bottom-2 right-2 bg-black/80 text-green-400 border-green-500/50">
                        {videoInfo.duration}
                      </Badge>
                    </div>
                    <div className="flex-1 p-4">
                      <h3 className="font-bold text-green-400 text-lg mb-2 line-clamp-2">
                        {videoInfo.title}
                      </h3>
                      <div className="space-y-1 text-sm text-green-600">
                        <p className="flex items-center gap-2">
                          <Youtube className="h-4 w-4" />
                          {videoInfo.channel}
                        </p>
                        <p className="flex items-center gap-2">
                          <Shield className="h-4 w-4" />
                          {videoInfo.viewCount} views
                        </p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        className="mt-3 border-green-500/50 text-green-400 hover:bg-green-500/10"
                        onClick={() => copyToClipboard(videoInfo.id)}
                      >
                        <Copy className="h-3 w-3 mr-1" />
                        Copy ID
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Download Options Tabs */}
            <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
              <Tabs defaultValue="video" className="w-full">
                <CardHeader className="pb-0">
                  <TabsList className="w-full grid grid-cols-4 bg-green-950/50 border border-green-500/30">
                    <TabsTrigger value="video" className="data-[state=active]:bg-green-500 data-[state=active]:text-black">
                      <Video className="h-4 w-4 mr-1" />
                      Video
                    </TabsTrigger>
                    <TabsTrigger value="audio" className="data-[state=active]:bg-green-500 data-[state=active]:text-black">
                      <Music className="h-4 w-4 mr-1" />
                      Audio
                    </TabsTrigger>
                    <TabsTrigger value="thumbnail" className="data-[state=active]:bg-green-500 data-[state=active]:text-black">
                      <Image className="h-4 w-4 mr-1" />
                      Thumb
                    </TabsTrigger>
                    <TabsTrigger value="subtitle" className="data-[state=active]:bg-green-500 data-[state=active]:text-black">
                      <Subtitles className="h-4 w-4 mr-1" />
                      Subs
                    </TabsTrigger>
                  </TabsList>
                </CardHeader>

                <CardContent className="pt-6">
                  {/* Video Tab */}
                  <TabsContent value="video" className="space-y-4 mt-0">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label className="text-green-400">Quality</Label>
                        <Select value={videoQuality} onValueChange={setVideoQuality}>
                          <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-black border-green-500/30 text-green-400">
                            {videoQualities.map((q) => (
                              <SelectItem key={q.value} value={q.value} className="hover:bg-green-500/10">
                                {q.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label className="text-green-400">Format</Label>
                        <Select value={videoFormat} onValueChange={setVideoFormat}>
                          <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-black border-green-500/30 text-green-400">
                            {videoFormats.map((f) => (
                              <SelectItem key={f.value} value={f.value} className="hover:bg-green-500/10">
                                {f.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <Button
                      onClick={() => startDownload("video")}
                      disabled={downloading || !url}
                      className="w-full bg-green-500 hover:bg-green-600 text-black font-semibold h-12"
                    >
                      {downloading ? (
                        <Loader2 className="h-5 w-5 animate-spin mr-2" />
                      ) : (
                        <Video className="h-5 w-5 mr-2" />
                      )}
                      Download Video
                    </Button>
                  </TabsContent>

                  {/* Audio Tab */}
                  <TabsContent value="audio" className="space-y-4 mt-0">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label className="text-green-400">Quality</Label>
                        <Select value={audioQuality} onValueChange={setAudioQuality}>
                          <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-black border-green-500/30 text-green-400">
                            {audioQualities.map((q) => (
                              <SelectItem key={q.value} value={q.value} className="hover:bg-green-500/10">
                                {q.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label className="text-green-400">Format</Label>
                        <Select value={audioFormat} onValueChange={setAudioFormat}>
                          <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-black border-green-500/30 text-green-400">
                            {audioFormats.map((f) => (
                              <SelectItem key={f.value} value={f.value} className="hover:bg-green-500/10">
                                {f.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <Button
                      onClick={() => startDownload("audio")}
                      disabled={downloading || !url}
                      className="w-full bg-green-500 hover:bg-green-600 text-black font-semibold h-12"
                    >
                      {downloading ? (
                        <Loader2 className="h-5 w-5 animate-spin mr-2" />
                      ) : (
                        <Music className="h-5 w-5 mr-2" />
                      )}
                      Download Audio
                    </Button>
                  </TabsContent>

                  {/* Thumbnail Tab */}
                  <TabsContent value="thumbnail" className="space-y-4 mt-0">
                    <p className="text-green-600 text-sm">
                      Download the video thumbnail in maximum available quality.
                    </p>
                    <Button
                      onClick={() => startDownload("thumbnail")}
                      disabled={downloading || !url}
                      className="w-full bg-green-500 hover:bg-green-600 text-black font-semibold h-12"
                    >
                      {downloading ? (
                        <Loader2 className="h-5 w-5 animate-spin mr-2" />
                      ) : (
                        <Image className="h-5 w-5 mr-2" />
                      )}
                      Download Thumbnail
                    </Button>
                  </TabsContent>

                  {/* Subtitle Tab */}
                  <TabsContent value="subtitle" className="space-y-4 mt-0">
                    <div className="space-y-2">
                      <Label className="text-green-400">Language</Label>
                      <Select value={subtitleLang} onValueChange={setSubtitleLang}>
                        <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-black border-green-500/30 text-green-400">
                          <SelectItem value="en">English</SelectItem>
                          <SelectItem value="hi">Hindi</SelectItem>
                          <SelectItem value="es">Spanish</SelectItem>
                          <SelectItem value="fr">French</SelectItem>
                          <SelectItem value="de">German</SelectItem>
                          <SelectItem value="ja">Japanese</SelectItem>
                          <SelectItem value="ko">Korean</SelectItem>
                          <SelectItem value="zh">Chinese</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <Button
                      onClick={() => startDownload("subtitle")}
                      disabled={downloading || !url}
                      className="w-full bg-green-500 hover:bg-green-600 text-black font-semibold h-12"
                    >
                      {downloading ? (
                        <Loader2 className="h-5 w-5 animate-spin mr-2" />
                      ) : (
                        <Subtitles className="h-5 w-5 mr-2" />
                      )}
                      Download Subtitles
                    </Button>
                  </TabsContent>
                </CardContent>
              </Tabs>
            </Card>

            {/* Download Progress */}
            {downloadProgress && (
              <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="text-green-400 text-sm flex items-center gap-2">
                    {downloadProgress.status === "complete" ? (
                      <CheckCircle2 className="h-4 w-4 text-green-400" />
                    ) : downloadProgress.status === "error" ? (
                      <AlertCircle className="h-4 w-4 text-red-400" />
                    ) : (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    )}
                    {downloadProgress.status === "complete"
                      ? "Download Complete"
                      : downloadProgress.status === "error"
                      ? "Download Failed"
                      : "Downloading..."}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {downloadProgress.status !== "error" && (
                    <div className="space-y-2">
                      <Progress
                        value={downloadProgress.progress}
                        className="h-2 bg-green-950 [&>div]:bg-green-500"
                      />
                      <div className="flex justify-between text-xs text-green-600">
                        <span>{downloadProgress.filename}</span>
                        <span>{downloadProgress.progress}%</span>
                      </div>
                    </div>
                  )}
                  {downloadProgress.status === "error" && (
                    <p className="text-red-400 text-sm">{downloadProgress.filename}</p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Panel - Features & History */}
          <div className="space-y-6">
            {/* Features Card */}
            <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-green-400 text-lg flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  FEATURES
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-48">
                  <ul className="space-y-2 text-sm text-green-400">
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      Multi-platform support
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      4K/8K video downloads
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      HDR video support
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      Audio extraction (320kbps)
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      Playlist downloads
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      Thumbnail embedding
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      Subtitle downloads
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      Metadata embedding
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      Batch downloads
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      Proxy support
                    </li>
                  </ul>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Supported Platforms */}
            <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-green-400 text-lg">PLATFORMS</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline" className="border-green-500/50 text-green-400">YouTube</Badge>
                  <Badge variant="outline" className="border-green-500/50 text-green-400">Twitch</Badge>
                  <Badge variant="outline" className="border-green-500/50 text-green-400">Twitter</Badge>
                  <Badge variant="outline" className="border-green-500/50 text-green-400">Instagram</Badge>
                  <Badge variant="outline" className="border-green-500/50 text-green-400">TikTok</Badge>
                  <Badge variant="outline" className="border-green-500/50 text-green-400">Facebook</Badge>
                  <Badge variant="outline" className="border-green-500/50 text-green-400">Vimeo</Badge>
                  <Badge variant="outline" className="border-green-500/50 text-green-400">Reddit</Badge>
                  <Badge variant="outline" className="border-green-500/50 text-green-400">+100 more</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Download History */}
            {downloadHistory.length > 0 && (
              <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-green-400 text-lg">HISTORY</CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDownloadHistory([])}
                    className="text-green-600 hover:text-green-400"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-32">
                    <ul className="space-y-2">
                      {downloadHistory.map((item, i) => (
                        <li key={i} className="text-xs text-green-600 flex items-center justify-between">
                          <span className="truncate flex-1">{item.title}</span>
                          <span className="text-green-700 ml-2">
                            {item.timestamp.toLocaleTimeString()}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}

            {/* Author Card */}
            <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
              <CardContent className="pt-6">
                <div className="text-center space-y-3">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20 border-2 border-green-500/50 mx-auto">
                    <Terminal className="h-8 w-8 text-green-400" />
                  </div>
                  <div>
                    <h3 className="font-bold text-green-400">RS (RAJSARASWATI JATAV)</h3>
                    <p className="text-xs text-green-600">LEGENDARY EXPERT</p>
                  </div>
                  <div className="flex justify-center gap-3">
                    <a
                      href="https://youtube.com/@T3rmuxk1ng"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-green-400 hover:text-green-300"
                    >
                      <Youtube className="h-5 w-5" />
                    </a>
                    <a
                      href="https://github.com/T3RMUXK1NG"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-green-400 hover:text-green-300"
                    >
                      <Github className="h-5 w-5" />
                    </a>
                  </div>
                  <p className="text-xs text-green-700">T3rmuxk1ng @ YouTube</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-green-500/30 py-6 mt-8">
        <div className="container mx-auto px-4 text-center text-green-600 text-sm">
          <p>Made with ❤️ by RS (T3rmuxk1ng)</p>
          <p className="text-xs mt-1">🔱 GOD MODE NEXUS v2.0 🔱</p>
        </div>
      </footer>
    </div>
  );
}
