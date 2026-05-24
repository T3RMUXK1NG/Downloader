"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { 
  Download, Music, Video, Image, FileText, Subtitles, Search, Settings, Github, Youtube, Zap, 
  Shield, Terminal, Loader2, CheckCircle2, AlertCircle, Trash2, ExternalLink, Copy, RefreshCw,
  Server, Smartphone, Info, Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Maximize,
  Minimize, RotateCcw, RotateCw, FlipHorizontal, FlipVertical, Crop, Scissors, Merge, Split,
  Wand2, Sparkles, Brain, Bot, MessageSquare, Bell, BellOff, Moon, Sun, Monitor, Palette,
  Layout, Grid, List, Folder, FolderOpen, File, FileArchive, FileAudio, FileVideo, FileImage,
  Cloud, CloudUpload, CloudDownload, CloudOff, Wifi, WifiOff, Bluetooth, Usb, HardDrive,
  Lock, Unlock, Key, Fingerprint, Eye, EyeOff, Filter, SortAsc, SortDesc, Calendar, Clock,
  Timer, Hourglass, Stopwatch, History, Bookmark, Star, Heart, ThumbsUp, ThumbsDown, Share2,
  Link, Link2, Unlink, Globe, Map, MapPin, Navigation, Compass, Radar, Radio, Tv, Film,
  Clapperboard, Presentation, Projector, Camera, CameraOff, Mic, MicOff, Headphones, Speaker,
  Disc, Album, RadioTower, Broadcast, Signal, Activity, TrendingUp, TrendingDown, BarChart3,
  PieChart, LineChart, AreaChart, Analytics, Dashboard, Gauge, Target, Crosshair, Focus,
  Scan, Maximize2, ZoomIn, ZoomOut, Move, MoveHorizontal, MoveVertical, ArrowUp, ArrowDown,
  ArrowLeft, ArrowRight, ArrowUpDown, ArrowLeftRight, ChevronsUp, ChevronsDown, ChevronUp,
  ChevronDown, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Menu, X, Plus, Minus,
  MoreHorizontal, MoreVertical, Settings2, SettingsIcon, Sliders, SlidersHorizontal, ToggleLeft,
  ToggleRight, Power, PowerOff, LogIn, LogOut, User, Users, UserPlus, UserMinus, UserCheck,
  UserX, ShieldCheck, ShieldAlert, ShieldQuestion, ShieldBan, AlertTriangle, AlertOctagon,
  Bug, BugOff, Code, Code2, TerminalSquare, Cpu, MemoryStick, Database, ServerCog, HardDriveDownload,
  Upload, DownloadCloud, RefreshCircuit, Binary, FileCode, FileSymlink, FolderArchive, FolderSync,
  FolderSearch, FolderX, FolderPlus, FolderMinus, FolderCog, FolderCheck, FolderLock, FolderHeart,
  Archive, ArchiveRestore, Package, PackageOpen, PackagePlus, PackageMinus, PackageCheck, PackageX,
  Layers, Stack, Boxes, Container, Inbox, Outbox, Send, Mail, MailOpen, MailCheck, MailX,
  MessageCircle, MessageSquarePlus, MessageCirclePlus, InboxArrowDown, InboxArrowUp, AtSign, Hash,
  Quote, Reply, ReplyAll, Forward, Phone, PhoneCall, PhoneOff, PhoneIncoming, PhoneOutgoing,
  VideoIcon, VideoOff, Videotape, ClapperboardIcon, FilmIcon, Music2, Music3, Music4, MusicIcon,
  Disc3, DiscAlbum, ListMusic, ListPlus, ListMinus, ListChecks, ListTodo, ListOrdered, ListX,
  Table, TableIcon, LayoutGrid, LayoutList, LayoutDashboard, LayoutTemplate, LayoutPanelTop,
  PanelTop, PanelBottom, PanelLeft, PanelRight, Sidebar, SidebarOpen, SidebarClose, MenuSquare,
  Square, SquareIcon, Circle, CircleIcon, Triangle, Diamond, Hexagon, Octagon, Pentagon, StarIcon,
  Award, Trophy, Medal, Crown, Gem, DiamondIcon, Flame, Fire, FlameKindling, Sparkle, SparklesIcon,
  PartyPopper, Confetti, Gift, GiftIcon, Cake, CakeIcon, Champagne, Candle, Celebration,
  Rocket, RocketIcon, Plane, PlaneIcon, Car, CarIcon, Bike, BikeIcon, Train, TrainIcon, Bus, BusIcon,
  Ship, ShipIcon, Anchor, AnchorIcon, Helicopter, HelicopterIcon, Satellite, SatelliteIcon, SatelliteDish,
  RadarIcon, Telescope, Binoculars, EyeIcon, Glasses, GlassesIcon, Contact, ContactIcon, IdCard,
  CreditCard, Wallet, Banknote, Coins, DollarSign, Cent, IndianRupee, Euro, PoundSterling, Yen,
  Bitcoin, Ethereum, Currency, Percent, PercentIcon, Divide, DivideIcon, Equal, EqualIcon, HashIcon,
  Calculator, CalculatorIcon, Abacus, Sigma, FunctionSquare, PieChartIcon, BarChart, BarChartIcon,
  LineChartIcon, AreaChartIcon, ScatterChart, RadarChart, RadialBarChart, TreemapChart, Heatmap,
  CandlestickChart, BoxChart, BoxSelect, BoxIcon, CircleDot, CircleDashed, CircleEqual, CircleSlash,
  CircleUser, CircleCheck, CircleX, CircleAlert, CircleHelp, CircleArrowLeft, CircleArrowRight,
  CircleArrowUp, CircleArrowDown, CirclePlus, CircleMinus, CirclePower, CircleStop, CirclePlay, CirclePause,
  ArrowUpCircle, ArrowDownCircle, ArrowLeftCircle, ArrowRightCircle, PlusCircle, MinusCircle,
  CheckCircle, XCircle, AlertCircleIcon, HelpCircle, PlayCircle, PauseCircle, StopCircle,
  Record, DiscIcon, SquarePlay, SquarePause, SquareCheck, SquareX, SquareArrowLeft, SquareArrowRight,
  SquareArrowUp, SquareArrowDown, SquarePlus, SquareMinus, SquareDashed, SquareSplitHorizontal,
  SquareSplitVertical, SquareStack, SquareM, SquareKanban, SquareFunction, SquareRadical, SquareAsterisk,
  TriangleAlert, TriangleRight, TriangleLeft, TriangleUp, TriangleDown, DiamondPlus, DiamondMinus,
  DiamondIconIcon, HexagonPlus, HexagonMinus, OctagonPlus, OctagonMinus, PentagonPlus, PentagonMinus
} from "lucide-react";
import { toast, Toaster } from "sonner";

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface VideoInfo {
  id: string;
  title: string;
  thumbnail: string;
  duration: string;
  channel: string;
  viewCount: string;
  description: string;
  uploadDate?: string;
  likes?: string;
  dislikes?: string;
  comments?: string;
  categories?: string[];
  tags?: string[];
  chapters?: { title: string; start: number; end: number }[];
  formats?: { format_id: string; ext: string; resolution: string; filesize: string }[];
  subtitles?: { code: string; name: string }[];
  isLive?: boolean;
  isAgeRestricted?: boolean;
}

interface DownloadProgress {
  status: "idle" | "starting" | "downloading" | "complete" | "error" | "paused" | "queued";
  progress: number;
  speed: string;
  eta: string;
  filename: string;
  size: string;
  downloaded: string;
}

interface DownloadItem {
  id: string;
  url: string;
  title: string;
  type: "video" | "audio" | "thumbnail" | "subtitle" | "playlist" | "batch";
  status: DownloadProgress["status"];
  progress: number;
  speed: string;
  eta: string;
  filename: string;
  size: string;
  downloaded: string;
  quality: string;
  format: string;
  timestamp: Date;
  error?: string;
}

interface PlaylistItem {
  id: string;
  title: string;
  thumbnail: string;
  duration: string;
  channel: string;
  selected: boolean;
}

interface ScheduledDownload {
  id: string;
  url: string;
  title: string;
  scheduledTime: Date;
  recurring: boolean;
  recurringPattern?: "daily" | "weekly" | "monthly";
  status: "pending" | "completed" | "cancelled";
}

interface DownloadSettings {
  // Video
  videoQuality: string;
  videoFormat: string;
  videoCodec: string;
  videoFps: string;
  hdrSupport: boolean;
  av1Support: boolean;
  
  // Audio
  audioQuality: string;
  audioFormat: string;
  audioCodec: string;
  audioChannels: string;
  audioSampleRate: string;
  embedThumbnail: boolean;
  embedMetadata: boolean;
  embedLyrics: boolean;
  
  // Subtitle
  subtitleLang: string;
  subtitleFormat: string;
  embedSubtitle: boolean;
  autoTranslate: boolean;
  translateLang: string;
  
  // Advanced
  downloadPath: string;
  filenameTemplate: string;
  maxConcurrent: number;
  speedLimit: number;
  proxyEnabled: boolean;
  proxyUrl: string;
  cookiesEnabled: boolean;
  cookiesPath: string;
  
  // Post-processing
  autoConvert: boolean;
  convertFormat: string;
  autoCompress: boolean;
  compressionLevel: number;
  autoWatermark: boolean;
  watermarkPath: string;
  autoTrim: boolean;
  trimStart: string;
  trimEnd: string;
  
  // Notifications
  notifyOnComplete: boolean;
  notifyOnError: boolean;
  soundEnabled: boolean;
  
  // Privacy
  incognitoMode: boolean;
  autoDelete: boolean;
  deleteAfterDays: number;
  encryptFiles: boolean;
  encryptionPassword: string;
}

interface ThemeSettings {
  mode: "dark" | "light" | "system";
  primaryColor: string;
  accentColor: string;
  backgroundColor: string;
  textColor: string;
  borderRadius: number;
  fontFamily: string;
  fontSize: number;
  animations: boolean;
  reducedMotion: boolean;
  matrixEffect: boolean;
  glowEffects: boolean;
  particleEffects: boolean;
}

interface UserPreferences {
  autoFetchInfo: boolean;
  autoPaste: boolean;
  confirmBeforeDownload: boolean;
  showAdvancedOptions: boolean;
  defaultTab: string;
  compactMode: boolean;
  showNotifications: boolean;
  saveHistory: boolean;
  maxHistoryItems: number;
  autoUpdate: boolean;
  betaFeatures: boolean;
  analyticsEnabled: boolean;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const VIDEO_QUALITIES = [
  { value: "8k", label: "8K Ultra HD (4320p)", icon: Crown },
  { value: "4k", label: "4K Ultra HD (2160p)", icon: Gem },
  { value: "1440p", label: "2K QHD (1440p)", icon: Award },
  { value: "1080p", label: "Full HD (1080p)", icon: Trophy },
  { value: "720p", label: "HD (720p)", icon: Medal },
  { value: "480p", label: "SD (480p)", icon: Star },
  { value: "360p", label: "Low (360p)", icon: StarIcon },
  { value: "240p", label: "Very Low (240p)", icon: Circle },
  { value: "best", label: "Best Available", icon: Zap },
  { value: "worst", label: "Smallest Size", icon: Minus },
];

const VIDEO_FORMATS = [
  { value: "mp4", label: "MP4", description: "Universal compatibility" },
  { value: "webm", label: "WebM", description: "Best for web" },
  { value: "mkv", label: "MKV", description: "Feature-rich container" },
  { value: "avi", label: "AVI", description: "Legacy support" },
  { value: "mov", label: "MOV", description: "Apple devices" },
  { value: "flv", label: "FLV", description: "Flash video" },
  { value: "wmv", label: "WMV", description: "Windows media" },
  { value: "ts", label: "TS", description: "Broadcast quality" },
];

const AUDIO_QUALITIES = [
  { value: "flac", label: "FLAC Lossless", bitrate: "~1400 kbps" },
  { value: "320", label: "320 kbps", bitrate: "High Quality" },
  { value: "256", label: "256 kbps", bitrate: "Good Quality" },
  { value: "192", label: "192 kbps", bitrate: "Normal Quality" },
  { value: "128", label: "128 kbps", bitrate: "Standard" },
  { value: "96", label: "96 kbps", bitrate: "Low Quality" },
  { value: "64", label: "64 kbps", bitrate: "Voice Quality" },
];

const AUDIO_FORMATS = [
  { value: "mp3", label: "MP3", description: "Universal" },
  { value: "m4a", label: "M4A/AAC", description: "Apple ecosystem" },
  { value: "flac", label: "FLAC", description: "Lossless" },
  { value: "opus", label: "Opus", description: "Best compression" },
  { value: "wav", label: "WAV", description: "Uncompressed" },
  { value: "ogg", label: "OGG Vorbis", description: "Open source" },
  { value: "aac", label: "AAC", description: "Efficient" },
  { value: "wma", label: "WMA", description: "Windows" },
];

const SUBTITLE_FORMATS = [
  { value: "srt", label: "SRT", description: "Most compatible" },
  { value: "vtt", label: "WebVTT", description: "Web standard" },
  { value: "ass", label: "ASS/SSA", description: "Advanced styling" },
  { value: "sub", label: "SUB", description: "MicroDVD" },
  { value: "sbv", label: "SBV", description: "YouTube format" },
];

const PLATFORMS = [
  { name: "YouTube", icon: Youtube, color: "#FF0000", features: ["video", "audio", "thumbnail", "subtitle", "playlist", "shorts", "live", "comments"] },
  { name: "YouTube Music", icon: Music, color: "#FF0000", features: ["audio", "playlist", "lyrics"] },
  { name: "Twitch", icon: Tv, color: "#9146FF", features: ["video", "audio", "clip", "chat", "vod"] },
  { name: "Twitter/X", icon: MessageCircle, color: "#1DA1F2", features: ["video", "audio", "gif", "image", "thread", "space"] },
  { name: "Instagram", icon: Camera, color: "#E4405F", features: ["video", "reel", "story", "image", "highlight", "igtv", "profile"] },
  { name: "TikTok", icon: Music2, color: "#000000", features: ["video", "audio", "no-watermark", "slideshow", "profile"] },
  { name: "Facebook", icon: Users, color: "#1877F2", features: ["video", "reel", "story", "image", "live"] },
  { name: "Vimeo", icon: Video, color: "#1AB7EA", features: ["video", "audio", "thumbnail"] },
  { name: "Reddit", icon: MessageSquare, color: "#FF4500", features: ["video", "audio", "gif", "image", "gallery"] },
  { name: "SoundCloud", icon: Headphones, color: "#FF5500", features: ["audio", "playlist", "thumbnail"] },
  { name: "Spotify", icon: Disc, color: "#1DB954", features: ["audio", "playlist", "podcast", "lyrics"] },
  { name: "Bilibili", icon: Tv, color: "#00A1D6", features: ["video", "audio", "subtitle", "danmaku"] },
  { name: "Dailymotion", icon: Play, color: "#00D2F3", features: ["video", "audio", "playlist"] },
  { name: "Pinterest", icon: Image, color: "#E60023", features: ["video", "image", "board"] },
  { name: "Tumblr", icon: Layout, color: "#36465D", features: ["video", "audio", "image", "gif"] },
  { name: "Vine", icon: Video, color: "#00BF8F", features: ["video", "audio"] },
  { name: "Periscope", icon: Radio, color: "#4081E0", features: ["video", "live"] },
  { name: "Mixer", icon: Gamepad2, color: "#002050", features: ["video", "live"] },
  { name: "Rumble", icon: Video, color: "#85C742", features: ["video", "audio"] },
  { name: "BitChute", icon: Video, color: "#EF5350", features: ["video", "audio"] },
  { name: "Odysee", icon: Disc, color: "#F4782D", features: ["video", "audio"] },
  { name: "DTube", icon: Video, color: "#FF6600", features: ["video", "audio"] },
  { name: "PeerTube", icon: Server, color: "#F1680D", features: ["video", "audio"] },
  { name: "TED", icon: Lightbulb, color: "#E62B1E", features: ["video", "subtitle"] },
  { name: "Viu", icon: Tv, color: "#FFD700", features: ["video", "subtitle"] },
  { name: "Hotstar", icon: Tv, color: "#0E4D92", features: ["video"] },
  { name: "Netflix", icon: Film, color: "#E50914", features: ["video", "subtitle"] },
  { name: "Prime Video", icon: Film, color: "#00A8E1", features: ["video", "subtitle"] },
  { name: "Disney+", icon: Sparkles, color: "#113CCF", features: ["video"] },
  { name: "HBO Max", icon: Tv, color: "#B206F9", features: ["video"] },
  { name: "Hulu", icon: Tv, color: "#1CE783", features: ["video"] },
  { name: "Apple TV+", icon: Tv, color: "#000000", features: ["video"] },
  { name: "Crunchyroll", icon: Tv, color: "#F47521", features: ["video", "subtitle"] },
  { name: "Funimation", icon: Tv, color: "#5B0BB5", features: ["video", "subtitle"] },
  { name: "Viki", icon: Tv, color: "#00A0E0", features: ["video", "subtitle"] },
  { name: "Dailymotion", icon: Play, color: "#0066DC", features: ["video"] },
  { name: "Aparat", icon: Play, color: "#E60023", features: ["video"] },
  { name: "OK.ru", icon: Users, color: "#EE8208", features: ["video", "audio"] },
  { name: "VK", icon: Users, color: "#4680C2", features: ["video", "audio", "image"] },
  { name: "Rutube", icon: Play, color: "#00AAFF", features: ["video"] },
  { name: "Mail.ru", icon: Mail, color: "#005FF9", features: ["video"] },
  { name: "Wistia", icon: Video, color: "#54BBFF", features: ["video"] },
  { name: "Brightcove", icon: Video, color: "#00A0E0", features: ["video"] },
  { name: "Kaltura", icon: Video, color: "#00A0E0", features: ["video"] },
  { name: "Panopto", icon: Video, color: "#00A0E0", features: ["video"] },
  { name: "Mediastream", icon: Video, color: "#00A0E0", features: ["video"] },
  { name: "Nebula", icon: Sparkles, color: "#7B2FF7", features: ["video"] },
  { name: "CuriosityStream", icon: Lightbulb, color: "#1A1A1A", features: ["video"] },
  { name: "Paramount+", icon: Tv, color: "#0064FF", features: ["video"] },
  { name: "Peacock", icon: Tv, color: "#000000", features: ["video"] },
  { name: "Discovery+", icon: Tv, color: "#00A0E0", features: ["video"] },
];

const FEATURE_CATEGORIES = [
  {
    category: "Download Features",
    icon: Download,
    features: [
      { name: "Multi-format video download", description: "MP4, WebM, MKV, AVI, MOV, FLV, WMV, TS" },
      { name: "Multi-format audio download", description: "MP3, M4A, FLAC, Opus, WAV, OGG, AAC, WMA" },
      { name: "8K/4K video support", description: "Download videos in stunning 8K and 4K resolution" },
      { name: "HDR video download", description: "Support for HDR, HDR10+, Dolby Vision" },
      { name: "60fps/120fps video", description: "High frame rate video downloads" },
      { name: "Lossless audio", description: "FLAC, WAV, ALAC lossless audio formats" },
      { name: "Audio quality selection", description: "320kbps, 256kbps, 192kbps, FLAC" },
      { name: "Video quality selection", description: "8K, 4K, 2K, 1080p, 720p, 480p, 360p" },
      { name: "Playlist download", description: "Download entire playlists with one click" },
      { name: "Channel download", description: "Download all videos from a channel" },
      { name: "Batch download", description: "Download multiple URLs simultaneously" },
      { name: "Queue management", description: "Manage download queue with priorities" },
      { name: "Concurrent downloads", description: "Download up to 16 files at once" },
      { name: "Resume downloads", description: "Resume interrupted downloads" },
      { name: "Download scheduling", description: "Schedule downloads for later" },
      { name: "Speed limiting", description: "Limit download speed to save bandwidth" },
      { name: "Proxy support", description: "Download through HTTP/SOCKS proxy" },
      { name: "Cookie authentication", description: "Use cookies for private content" },
      { name: "Subtitle download", description: "Download subtitles in multiple languages" },
      { name: "Subtitle embedding", description: "Burn subtitles into video" },
      { name: "Thumbnail download", description: "Download video thumbnails" },
      { name: "Thumbnail embedding", description: "Embed thumbnail in audio files" },
      { name: "Metadata embedding", description: "Add metadata to downloaded files" },
      { name: "Chapter support", description: "Download videos with chapters" },
      { name: "Live stream download", description: "Download live streams in real-time" },
      { name: "VOD download", description: "Download past broadcasts/VODs" },
      { name: "Clip download", description: "Download specific portions of videos" },
      { name: "Audio-only live", description: "Download audio from live streams" },
      { name: "Story download", description: "Download stories from Instagram, etc." },
      { name: "Reel download", description: "Download reels/shorts content" },
      { name: "No watermark", description: "Download TikTok without watermark" },
      { name: "Slideshow download", description: "Download TikTok photo slideshows" },
      { name: "Thread download", description: "Download Twitter/X threads" },
      { name: "Gallery download", description: "Download image galleries" },
      { name: "GIF download", description: "Download animated GIFs" },
      { name: "Profile picture", description: "Download profile pictures in HD" },
      { name: "Highlight download", description: "Download Instagram highlights" },
      { name: "IGTV download", description: "Download IGTV videos" },
      { name: "Space download", description: "Download Twitter/X Spaces" },
      { name: "Chat download", description: "Download Twitch chat logs" },
      { name: "Danmaku download", description: "Download Bilibili danmaku" },
      { name: "Lyrics download", description: "Download song lyrics" },
      { name: "Podcast download", description: "Download podcast episodes" },
      { name: "Audiobook download", description: "Download audiobooks" },
      { name: "Radio download", description: "Download radio streams" },
      { name: "Podcast RSS", description: "Parse and download from RSS feeds" },
      { name: "M3U8 download", description: "Download HLS streaming videos" },
      { name: "DASH download", description: "Download DASH streaming videos" },
      { name: "RTMP download", description: "Download RTMP streams" },
      { name: "FTP download", description: "Download files from FTP servers" },
      { name: "Direct URL", description: "Download from direct file URLs" },
    ]
  },
  {
    category: "Video Processing",
    icon: Video,
    features: [
      { name: "Video trimming", description: "Cut specific portions of videos" },
      { name: "Video merging", description: "Combine multiple videos" },
      { name: "Video splitting", description: "Split video into parts" },
      { name: "Video compression", description: "Reduce video file size" },
      { name: "Format conversion", description: "Convert between video formats" },
      { name: "Resolution scaling", description: "Upscale or downscale videos" },
      { name: "Frame rate conversion", description: "Change video frame rate" },
      { name: "Video cropping", description: "Crop video dimensions" },
      { name: "Video rotation", description: "Rotate video 90/180/270 degrees" },
      { name: "Video flipping", description: "Flip video horizontally/vertically" },
      { name: "Watermark addition", description: "Add custom watermarks" },
      { name: "Text overlay", description: "Add text to videos" },
      { name: "Subtitle burn", description: "Permanently add subtitles" },
      { name: "Audio replacement", description: "Replace video audio" },
      { name: "Audio extraction", description: "Extract audio from video" },
      { name: "Video stabilization", description: "Stabilize shaky footage" },
      { name: "Denoise video", description: "Remove video noise" },
      { name: "Color correction", description: "Adjust brightness, contrast, saturation" },
      { name: "Video filters", description: "Apply various visual filters" },
      { name: "Speed adjustment", description: "Speed up or slow down videos" },
      { name: "Reverse video", description: "Play video backwards" },
      { name: "GIF creation", description: "Convert video to GIF" },
      { name: "WebM animation", description: "Create WebM animations" },
      { name: "Video thumbnails", description: "Generate thumbnail grid" },
      { name: "Video preview", description: "Create preview clips" },
      { name: "Scene detection", description: "Detect and split scenes" },
      { name: "Black frame detection", description: "Detect black frames" },
      { name: "Silence detection", description: "Detect silent portions" },
      { name: "Video deduplication", description: "Remove duplicate frames" },
      { name: "Keyframe extraction", description: "Extract keyframes" },
    ]
  },
  {
    category: "Audio Processing",
    icon: Music,
    features: [
      { name: "Audio trimming", description: "Cut specific portions of audio" },
      { name: "Audio merging", description: "Combine multiple audio files" },
      { name: "Audio splitting", description: "Split audio into parts" },
      { name: "Audio compression", description: "Reduce audio file size" },
      { name: "Format conversion", description: "Convert between audio formats" },
      { name: "Bitrate adjustment", description: "Change audio bitrate" },
      { name: "Sample rate conversion", description: "Change audio sample rate" },
      { name: "Channel conversion", description: "Convert stereo to mono and vice versa" },
      { name: "Volume normalization", description: "Normalize audio volume" },
      { name: "Volume adjustment", description: "Increase or decrease volume" },
      { name: "Fade in/out", description: "Add fade effects" },
      { name: "Speed adjustment", description: "Speed up or slow down audio" },
      { name: "Pitch adjustment", description: "Change audio pitch" },
      { name: "Reverse audio", description: "Play audio backwards" },
      { name: "Audio enhancement", description: "Enhance audio quality" },
      { name: "Noise reduction", description: "Remove background noise" },
      { name: "Vocal removal", description: "Remove vocals from songs" },
      { name: "Instrumental extraction", description: "Extract instrumentals" },
      { name: "Bass boost", description: "Enhance bass frequencies" },
      { name: "Treble boost", description: "Enhance treble frequencies" },
      { name: "Equalizer", description: "Adjust frequency bands" },
      { name: "Echo/reverb", description: "Add echo or reverb effects" },
      { name: "Audio visualization", description: "Generate audio waveforms" },
      { name: "Spectrum analysis", description: "Analyze audio spectrum" },
      { name: "BPM detection", description: "Detect beats per minute" },
      { name: "Key detection", description: "Detect musical key" },
      { name: "Silence removal", description: "Remove silent portions" },
      { name: "Auto-duck", description: "Automatic volume ducking" },
      { name: "Loudness normalization", description: "EBU R128 loudness" },
      { name: "True peak limiting", description: "Prevent clipping" },
    ]
  },
  {
    category: "Image Processing",
    icon: Image,
    features: [
      { name: "Format conversion", description: "Convert between image formats" },
      { name: "Image compression", description: "Reduce image file size" },
      { name: "Image resizing", description: "Resize images to specific dimensions" },
      { name: "Image cropping", description: "Crop images" },
      { name: "Image rotation", description: "Rotate images" },
      { name: "Image flipping", description: "Flip images horizontally/vertically" },
      { name: "Watermark addition", description: "Add watermarks to images" },
      { name: "Text overlay", description: "Add text to images" },
      { name: "Image filters", description: "Apply various filters" },
      { name: "Color adjustment", description: "Adjust brightness, contrast, saturation" },
      { name: "Background removal", description: "Remove image backgrounds" },
      { name: "Image upscaling", description: "AI-powered image upscaling" },
      { name: "Noise reduction", description: "Remove image noise" },
      { name: "Sharpening", description: "Sharpen blurry images" },
      { name: "Blur effects", description: "Apply blur effects" },
      { name: "Border addition", description: "Add borders to images" },
      { name: "Round corners", description: "Add rounded corners" },
      { name: "Shadow effects", description: "Add drop shadows" },
      { name: "Collage creation", description: "Create image collages" },
      { name: "Batch processing", description: "Process multiple images at once" },
    ]
  },
  {
    category: "AI Features",
    icon: Brain,
    features: [
      { name: "Smart recommendations", description: "AI-powered content suggestions" },
      { name: "Auto-subtitle generation", description: "Generate subtitles using AI" },
      { name: "Auto-translation", description: "Translate subtitles automatically" },
      { name: "Content summarization", description: "AI-generated video summaries" },
      { name: "Smart filename", description: "Auto-generate descriptive filenames" },
      { name: "Content categorization", description: "Auto-categorize downloads" },
      { name: "Duplicate detection", description: "Detect duplicate content" },
      { name: "Quality prediction", description: "Predict video quality" },
      { name: "Scene recognition", description: "AI scene detection" },
      { name: "Object detection", description: "Detect objects in videos" },
      { name: "Face detection", description: "Detect faces in media" },
      { name: "Text recognition", description: "OCR for images/videos" },
      { name: "Sentiment analysis", description: "Analyze content sentiment" },
      { name: "Thumbnail generation", description: "AI-powered thumbnail creation" },
      { name: "Voice enhancement", description: "AI voice enhancement" },
      { name: "Background removal", description: "AI background removal" },
      { name: "Video upscaling", description: "AI video upscaling" },
      { name: "Frame interpolation", description: "AI frame interpolation" },
      { name: "Colorization", description: "Colorize black and white videos" },
      { name: "Noise reduction", description: "AI-powered noise reduction" },
    ]
  },
  {
    category: "Cloud & Storage",
    icon: Cloud,
    features: [
      { name: "Google Drive sync", description: "Sync with Google Drive" },
      { name: "Dropbox sync", description: "Sync with Dropbox" },
      { name: "OneDrive sync", description: "Sync with OneDrive" },
      { name: "iCloud sync", description: "Sync with iCloud" },
      { name: "Mega integration", description: "Upload to Mega" },
      { name: "pCloud integration", description: "Upload to pCloud" },
      { name: "Box integration", description: "Upload to Box" },
      { name: "WebDAV support", description: "Connect via WebDAV" },
      { name: "FTP upload", description: "Upload via FTP" },
      { name: "SFTP upload", description: "Upload via SFTP" },
      { name: "S3 compatible", description: "Upload to S3-compatible storage" },
      { name: "Self-hosted cloud", description: "Connect to Nextcloud/ownCloud" },
      { name: "Network storage", description: "Connect to NAS/SMB shares" },
      { name: "Auto-backup", description: "Automatic backup to cloud" },
      { name: "Selective sync", description: "Choose what to sync" },
      { name: "Offline mode", description: "Access downloads offline" },
      { name: "Storage analytics", description: "Track storage usage" },
      { name: "Auto-cleanup", description: "Automatically delete old files" },
    ]
  },
  {
    category: "Privacy & Security",
    icon: Shield,
    features: [
      { name: "Password protection", description: "Protect app with password" },
      { name: "Biometric unlock", description: "Fingerprint/Face ID unlock" },
      { name: "Incognito mode", description: "Download without history" },
      { name: "Encrypted storage", description: "Encrypt downloaded files" },
      { name: "Secure delete", description: "Securely delete files" },
      { name: "VPN integration", description: "Download through VPN" },
      { name: "Proxy support", description: "Anonymous downloading" },
      { name: "No logs mode", description: "Don't store any logs" },
      { name: "Private browsing", description: "Browse without tracking" },
      { name: "Cookie management", description: "Manage cookies" },
      { name: "Data export", description: "Export your data" },
      { name: "Data deletion", description: "Delete all data" },
    ]
  },
  {
    category: "Organization",
    icon: Folder,
    features: [
      { name: "Custom folders", description: "Create custom download folders" },
      { name: "Auto-organize", description: "Automatically organize downloads" },
      { name: "Tags & labels", description: "Tag your downloads" },
      { name: "Smart folders", description: "Auto-sort based on rules" },
      { name: "Search & filter", description: "Find downloads quickly" },
      { name: "Favorites", description: "Mark favorites" },
      { name: "Playlists", description: "Create custom playlists" },
      { name: "Watch later", description: "Save for later" },
      { name: "Download history", description: "Track all downloads" },
      { name: "Statistics", description: "View download stats" },
      { name: "Export/import", description: "Export/import settings" },
      { name: "Backup/restore", description: "Backup and restore data" },
    ]
  },
  {
    category: "Notifications",
    icon: Bell,
    features: [
      { name: "Push notifications", description: "Get notified on mobile" },
      { name: "Email notifications", description: "Email alerts" },
      { name: "Discord webhook", description: "Discord notifications" },
      { name: "Telegram bot", description: "Telegram notifications" },
      { name: "Slack integration", description: "Slack notifications" },
      { name: "Custom webhook", description: "Custom webhook support" },
      { name: "Sound alerts", description: "Custom sound alerts" },
      { name: "Do not disturb", description: "Mute notifications" },
    ]
  },
  {
    category: "UI/UX",
    icon: Palette,
    features: [
      { name: "Dark mode", description: "Beautiful dark theme" },
      { name: "Light mode", description: "Clean light theme" },
      { name: "Auto theme", description: "Follow system theme" },
      { name: "Custom themes", description: "Create custom themes" },
      { name: "Color schemes", description: "Multiple color options" },
      { name: "Compact mode", description: "Compact layout" },
      { name: "Large text", description: "Accessibility option" },
      { name: "Animations", description: "Smooth animations" },
      { name: "Reduced motion", description: "Minimize animations" },
      { name: "Matrix effect", description: "Matrix-style background" },
      { name: "Glow effects", description: "Neon glow effects" },
      { name: "Custom fonts", description: "Choose your font" },
      { name: "Drag & drop", description: "Drag and drop support" },
      { name: "Keyboard shortcuts", description: "Quick actions" },
      { name: "Touch gestures", description: "Mobile gestures" },
      { name: "Voice commands", description: "Control with voice" },
    ]
  },
  {
    category: "Advanced Tools",
    icon: Settings,
    features: [
      { name: "Custom commands", description: "Run custom yt-dlp commands" },
      { name: "Script editor", description: "Create automation scripts" },
      { name: "API access", description: "REST API for automation" },
      { name: "CLI mode", description: "Command-line interface" },
      { name: "Batch processing", description: "Process multiple files" },
      { name: "Templates", description: "Save download templates" },
      { name: "Presets", description: "Quick quality presets" },
      { name: "Auto-rules", description: "Automatic processing rules" },
      { name: "Watch folders", description: "Monitor folders for URLs" },
      { name: "RSS feeds", description: "Subscribe to RSS feeds" },
      { name: "Browser extension", description: "Browser integration" },
      { name: "Context menu", description: "Right-click to download" },
    ]
  }
];

// Missing import
const Gamepad2 = Tv;
const Lightbulb = Zap;

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function RSDownloaderApp() {
  // State management
  const [url, setUrl] = useState("");
  const [urls, setUrls] = useState<string[]>([]);
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<DownloadProgress | null>(null);
  const [downloadHistory, setDownloadHistory] = useState<DownloadItem[]>([]);
  const [downloadQueue, setDownloadQueue] = useState<DownloadItem[]>([]);
  const [playlistItems, setPlaylistItems] = useState<PlaylistItem[]>([]);
  const [scheduledDownloads, setScheduledDownloads] = useState<ScheduledDownload[]>([]);
  
  // Server configuration
  const [serverUrl, setServerUrl] = useState("");
  const [showServerConfig, setShowServerConfig] = useState(false);
  const [serverStatus, setServerStatus] = useState<"unknown" | "connected" | "disconnected">("unknown");
  
  // UI State
  const [activeTab, setActiveTab] = useState("download");
  const [showSettings, setShowSettings] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [theme, setTheme] = useState<ThemeSettings>({
    mode: "dark",
    primaryColor: "#22c55e",
    accentColor: "#10b981",
    backgroundColor: "#000000",
    textColor: "#22c55e",
    borderRadius: 8,
    fontFamily: "inter",
    fontSize: 14,
    animations: true,
    reducedMotion: false,
    matrixEffect: true,
    glowEffects: true,
    particleEffects: false,
  });
  
  // Settings
  const [settings, setSettings] = useState<DownloadSettings>({
    videoQuality: "1080p",
    videoFormat: "mp4",
    videoCodec: "h264",
    videoFps: "auto",
    hdrSupport: false,
    av1Support: false,
    audioQuality: "320",
    audioFormat: "mp3",
    audioCodec: "aac",
    audioChannels: "stereo",
    audioSampleRate: "48000",
    embedThumbnail: true,
    embedMetadata: true,
    embedLyrics: false,
    subtitleLang: "en",
    subtitleFormat: "srt",
    embedSubtitle: false,
    autoTranslate: false,
    translateLang: "en",
    downloadPath: "/downloads",
    filenameTemplate: "%(title)s-%(id)s.%(ext)s",
    maxConcurrent: 3,
    speedLimit: 0,
    proxyEnabled: false,
    proxyUrl: "",
    cookiesEnabled: false,
    cookiesPath: "",
    autoConvert: false,
    convertFormat: "mp4",
    autoCompress: false,
    compressionLevel: 5,
    autoWatermark: false,
    watermarkPath: "",
    autoTrim: false,
    trimStart: "00:00:00",
    trimEnd: "00:00:00",
    notifyOnComplete: true,
    notifyOnError: true,
    soundEnabled: true,
    incognitoMode: false,
    autoDelete: false,
    deleteAfterDays: 30,
    encryptFiles: false,
    encryptionPassword: "",
  });
  
  // Preferences
  const [preferences, setPreferences] = useState<UserPreferences>({
    autoFetchInfo: true,
    autoPaste: false,
    confirmBeforeDownload: true,
    showAdvancedOptions: false,
    defaultTab: "download",
    compactMode: false,
    showNotifications: true,
    saveHistory: true,
    maxHistoryItems: 100,
    autoUpdate: true,
    betaFeatures: false,
    analyticsEnabled: false,
  });

  // Load saved settings on mount
  useEffect(() => {
    const savedServer = localStorage.getItem("rs-downloader-server");
    const savedSettings = localStorage.getItem("rs-downloader-settings");
    const savedTheme = localStorage.getItem("rs-downloader-theme");
    const savedPreferences = localStorage.getItem("rs-downloader-preferences");
    
    if (savedServer) {
      setServerUrl(savedServer);
      checkServerConnection(savedServer);
    }
    if (savedSettings) {
      setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
    }
    if (savedTheme) {
      setTheme(prev => ({ ...prev, ...JSON.parse(savedTheme) }));
    }
    if (savedPreferences) {
      setPreferences(prev => ({ ...prev, ...JSON.parse(savedPreferences) }));
    }
  }, []);

  // Save settings whenever they change
  useEffect(() => {
    localStorage.setItem("rs-downloader-settings", JSON.stringify(settings));
  }, [settings]);

  useEffect(() => {
    localStorage.setItem("rs-downloader-theme", JSON.stringify(theme));
  }, [theme]);

  useEffect(() => {
    localStorage.setItem("rs-downloader-preferences", JSON.stringify(preferences));
  }, [preferences]);

  const checkServerConnection = async (server: string) => {
    try {
      const response = await fetch(`${server}/api/info`, { method: "OPTIONS" });
      setServerStatus(response.ok ? "connected" : "disconnected");
    } catch {
      setServerStatus("disconnected");
    }
  };

  const saveServerUrl = () => {
    if (serverUrl) {
      localStorage.setItem("rs-downloader-server", serverUrl);
      checkServerConnection(serverUrl);
      setShowServerConfig(false);
      toast.success("Server URL saved!");
    }
  };

  const getApiBase = () => serverUrl || "";

  const fetchVideoInfo = async () => {
    if (!url) {
      toast.error("Please enter a URL");
      return;
    }
    if (!serverUrl) {
      toast.error("Please configure server URL first");
      setShowServerConfig(true);
      return;
    }

    setLoading(true);
    setVideoInfo(null);

    try {
      const response = await fetch(`${getApiBase()}/api/info`, {
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
    } catch {
      toast.error("Failed to connect to server");
      setServerStatus("disconnected");
    } finally {
      setLoading(false);
    }
  };

  const startDownload = async (type: "video" | "audio" | "thumbnail" | "subtitle") => {
    if (!url) {
      toast.error("Please enter a URL");
      return;
    }
    if (!serverUrl) {
      toast.error("Please configure server URL first");
      setShowServerConfig(true);
      return;
    }

    setDownloading(true);
    setDownloadProgress({ status: "starting", progress: 0, speed: "", eta: "", filename: "", size: "", downloaded: "" });

    try {
      const body: Record<string, unknown> = { url, type };

      if (type === "video") {
        body.quality = settings.videoQuality;
        body.format = settings.videoFormat;
      } else if (type === "audio") {
        body.quality = settings.audioQuality;
        body.format = settings.audioFormat;
        body.embedThumbnail = settings.embedThumbnail;
      } else if (type === "subtitle") {
        body.language = settings.subtitleLang;
      }

      const response = await fetch(`${getApiBase()}/api/download`, {
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
          size: "",
          downloaded: "",
        });
        
        if (preferences.saveHistory) {
          const newHistoryItem: DownloadItem = {
            id: Date.now().toString(),
            url,
            title: videoInfo?.title || "Unknown",
            type,
            status: "complete",
            progress: 100,
            speed: "",
            eta: "",
            filename: data.filename || "download",
            size: "",
            downloaded: "",
            quality: type === "video" ? settings.videoQuality : settings.audioQuality,
            format: type === "video" ? settings.videoFormat : settings.audioFormat,
            timestamp: new Date(),
          };
          setDownloadHistory(prev => [newHistoryItem, ...prev.slice(0, preferences.maxHistoryItems - 1)]);
        }
        
        toast.success("Download complete!");
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
          size: "",
          downloaded: "",
        });
        toast.error(data.error || "Download failed");
      }
    } catch {
      toast.error("Failed to start download");
      setDownloadProgress({
        status: "error",
        progress: 0,
        speed: "",
        eta: "",
        filename: "Connection error",
        size: "",
        downloaded: "",
      });
      setServerStatus("disconnected");
    } finally {
      setDownloading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  // Calculate total features
  const totalFeatures = useMemo(() => {
    return FEATURE_CATEGORIES.reduce((acc, cat) => acc + cat.features.length, 0);
  }, []);

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-black text-green-400">
        {/* Matrix-style background */}
        {theme.matrixEffect && (
          <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-5">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_#00ff00_1px,_transparent_1px)] bg-[length:20px_20px]" />
          </div>
        )}

        {/* Header */}
        <header className="sticky top-0 z-50 border-b border-green-500/30 bg-black/90 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/20 border border-green-500/50 ${theme.glowEffects ? 'shadow-lg shadow-green-500/20' : ''}`}>
                  <Terminal className="h-6 w-6 text-green-400" />
                </div>
                <div>
                  <h1 className="text-xl font-bold tracking-wider text-green-400">
                    RS DOWNLOADER
                  </h1>
                  <p className="text-xs text-green-600">v3.0.0 ULTIMATE NEXUS • {totalFeatures}+ FEATURES</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* Server Status */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowServerConfig(true)}
                  className={`border-green-500/50 ${serverStatus === "connected" ? "text-green-400" : serverStatus === "disconnected" ? "text-red-400" : "text-yellow-400"}`}
                >
                  <Server className="h-4 w-4 mr-1" />
                  {serverStatus === "connected" ? "Connected" : serverStatus === "disconnected" ? "Disconnected" : "Setup"}
                </Button>
                
                {/* Theme Toggle */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setTheme(prev => ({ ...prev, mode: prev.mode === "dark" ? "light" : "dark" }))}
                  className="border-green-500/50 text-green-400"
                >
                  {theme.mode === "dark" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                </Button>
                
                {/* Settings */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowSettings(true)}
                  className="border-green-500/50 text-green-400"
                >
                  <Settings className="h-4 w-4" />
                </Button>
                
                <Badge variant="outline" className="border-green-500/50 text-green-400">
                  <Smartphone className="h-3 w-3 mr-1" />
                  APK
                </Badge>
              </div>
            </div>
          </div>
        </header>

        {/* Server Configuration Modal */}
        {showServerConfig && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4">
            <Card className="border-green-500/30 bg-black w-full max-w-md">
              <CardHeader>
                <CardTitle className="text-green-400 flex items-center gap-2">
                  <Server className="h-5 w-5" />
                  SERVER CONFIGURATION
                </CardTitle>
                <CardDescription className="text-green-600">
                  Enter your RS Downloader server URL to connect
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-green-400">Server URL</Label>
                  <Input
                    type="url"
                    placeholder="http://192.168.1.100:3000 or https://your-server.com"
                    value={serverUrl}
                    onChange={(e) => setServerUrl(e.target.value)}
                    className="bg-black/50 border-green-500/30 text-green-400 placeholder:text-green-700 focus:border-green-500"
                  />
                </div>
                <div className="bg-green-950/30 border border-green-500/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <Info className="h-4 w-4 text-green-400 mt-0.5 shrink-0" />
                    <div className="text-xs text-green-600 space-y-2">
                      <p><strong className="text-green-400">How to use:</strong></p>
                      <p>1. Run RS Downloader server on your PC/Server</p>
                      <p>2. Enter the server URL above</p>
                      <p>3. Make sure your device is on the same network</p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={saveServerUrl} className="flex-1 bg-green-500 hover:bg-green-600 text-black font-semibold">
                    Save & Connect
                  </Button>
                  <Button variant="outline" onClick={() => setShowServerConfig(false)} className="border-green-500/50 text-green-400">
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Settings Sheet */}
        <Sheet open={showSettings} onOpenChange={setShowSettings}>
          <SheetContent className="bg-black border-green-500/30 text-green-400 w-full sm:max-w-lg overflow-y-auto">
            <SheetHeader>
              <SheetTitle className="text-green-400 flex items-center gap-2">
                <Settings className="h-5 w-5" />
                SETTINGS
              </SheetTitle>
              <SheetDescription className="text-green-600">
                Customize your download experience
              </SheetDescription>
            </SheetHeader>
            
            <div className="mt-6 space-y-6">
              {/* Video Settings */}
              <Accordion type="single" collapsible defaultValue="video">
                <AccordionItem value="video" className="border-green-500/30">
                  <AccordionTrigger className="text-green-400 hover:text-green-300">
                    <div className="flex items-center gap-2">
                      <Video className="h-4 w-4" />
                      Video Settings
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-4">
                    <div className="space-y-2">
                      <Label className="text-green-400 text-sm">Quality</Label>
                      <Select value={settings.videoQuality} onValueChange={(v) => setSettings(prev => ({ ...prev, videoQuality: v }))}>
                        <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-black border-green-500/30">
                          {VIDEO_QUALITIES.map((q) => (
                            <SelectItem key={q.value} value={q.value} className="text-green-400 hover:bg-green-500/10">
                              {q.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-green-400 text-sm">Format</Label>
                      <Select value={settings.videoFormat} onValueChange={(v) => setSettings(prev => ({ ...prev, videoFormat: v }))}>
                        <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-black border-green-500/30">
                          {VIDEO_FORMATS.map((f) => (
                            <SelectItem key={f.value} value={f.value} className="text-green-400 hover:bg-green-500/10">
                              {f.label} - {f.description}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">HDR Support</Label>
                      <Switch checked={settings.hdrSupport} onCheckedChange={(v) => setSettings(prev => ({ ...prev, hdrSupport: v }))} />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">AV1 Codec</Label>
                      <Switch checked={settings.av1Support} onCheckedChange={(v) => setSettings(prev => ({ ...prev, av1Support: v }))} />
                    </div>
                  </AccordionContent>
                </AccordionItem>

                {/* Audio Settings */}
                <AccordionItem value="audio" className="border-green-500/30">
                  <AccordionTrigger className="text-green-400 hover:text-green-300">
                    <div className="flex items-center gap-2">
                      <Music className="h-4 w-4" />
                      Audio Settings
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-4">
                    <div className="space-y-2">
                      <Label className="text-green-400 text-sm">Quality</Label>
                      <Select value={settings.audioQuality} onValueChange={(v) => setSettings(prev => ({ ...prev, audioQuality: v }))}>
                        <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-black border-green-500/30">
                          {AUDIO_QUALITIES.map((q) => (
                            <SelectItem key={q.value} value={q.value} className="text-green-400 hover:bg-green-500/10">
                              {q.label} {q.bitrate ? `(${q.bitrate})` : ''}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-green-400 text-sm">Format</Label>
                      <Select value={settings.audioFormat} onValueChange={(v) => setSettings(prev => ({ ...prev, audioFormat: v }))}>
                        <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-black border-green-500/30">
                          {AUDIO_FORMATS.map((f) => (
                            <SelectItem key={f.value} value={f.value} className="text-green-400 hover:bg-green-500/10">
                              {f.label} - {f.description}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">Embed Thumbnail</Label>
                      <Switch checked={settings.embedThumbnail} onCheckedChange={(v) => setSettings(prev => ({ ...prev, embedThumbnail: v }))} />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">Embed Metadata</Label>
                      <Switch checked={settings.embedMetadata} onCheckedChange={(v) => setSettings(prev => ({ ...prev, embedMetadata: v }))} />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">Embed Lyrics</Label>
                      <Switch checked={settings.embedLyrics} onCheckedChange={(v) => setSettings(prev => ({ ...prev, embedLyrics: v }))} />
                    </div>
                  </AccordionContent>
                </AccordionItem>

                {/* Subtitle Settings */}
                <AccordionItem value="subtitle" className="border-green-500/30">
                  <AccordionTrigger className="text-green-400 hover:text-green-300">
                    <div className="flex items-center gap-2">
                      <Subtitles className="h-4 w-4" />
                      Subtitle Settings
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-4">
                    <div className="space-y-2">
                      <Label className="text-green-400 text-sm">Language</Label>
                      <Select value={settings.subtitleLang} onValueChange={(v) => setSettings(prev => ({ ...prev, subtitleLang: v }))}>
                        <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-black border-green-500/30">
                          <SelectItem value="en" className="text-green-400">English</SelectItem>
                          <SelectItem value="hi" className="text-green-400">Hindi</SelectItem>
                          <SelectItem value="es" className="text-green-400">Spanish</SelectItem>
                          <SelectItem value="fr" className="text-green-400">French</SelectItem>
                          <SelectItem value="de" className="text-green-400">German</SelectItem>
                          <SelectItem value="ja" className="text-green-400">Japanese</SelectItem>
                          <SelectItem value="ko" className="text-green-400">Korean</SelectItem>
                          <SelectItem value="zh" className="text-green-400">Chinese</SelectItem>
                          <SelectItem value="ar" className="text-green-400">Arabic</SelectItem>
                          <SelectItem value="pt" className="text-green-400">Portuguese</SelectItem>
                          <SelectItem value="ru" className="text-green-400">Russian</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-green-400 text-sm">Format</Label>
                      <Select value={settings.subtitleFormat} onValueChange={(v) => setSettings(prev => ({ ...prev, subtitleFormat: v }))}>
                        <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-black border-green-500/30">
                          {SUBTITLE_FORMATS.map((f) => (
                            <SelectItem key={f.value} value={f.value} className="text-green-400 hover:bg-green-500/10">
                              {f.label} - {f.description}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">Auto Translate</Label>
                      <Switch checked={settings.autoTranslate} onCheckedChange={(v) => setSettings(prev => ({ ...prev, autoTranslate: v }))} />
                    </div>
                  </AccordionContent>
                </AccordionItem>

                {/* Advanced Settings */}
                <AccordionItem value="advanced" className="border-green-500/30">
                  <AccordionTrigger className="text-green-400 hover:text-green-300">
                    <div className="flex items-center gap-2">
                      <Sliders className="h-4 w-4" />
                      Advanced
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-4">
                    <div className="space-y-2">
                      <Label className="text-green-400 text-sm">Max Concurrent Downloads: {settings.maxConcurrent}</Label>
                      <Slider value={[settings.maxConcurrent]} onValueChange={(v) => setSettings(prev => ({ ...prev, maxConcurrent: v[0] }))} min={1} max={16} step={1} />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-green-400 text-sm">Speed Limit (KB/s, 0 = unlimited): {settings.speedLimit}</Label>
                      <Slider value={[settings.speedLimit]} onValueChange={(v) => setSettings(prev => ({ ...prev, speedLimit: v[0] }))} min={0} max={10000} step={100} />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">Proxy Enabled</Label>
                      <Switch checked={settings.proxyEnabled} onCheckedChange={(v) => setSettings(prev => ({ ...prev, proxyEnabled: v }))} />
                    </div>
                    {settings.proxyEnabled && (
                      <div className="space-y-2">
                        <Label className="text-green-400 text-sm">Proxy URL</Label>
                        <Input
                          placeholder="http://proxy:port or socks5://proxy:port"
                          value={settings.proxyUrl}
                          onChange={(e) => setSettings(prev => ({ ...prev, proxyUrl: e.target.value }))}
                          className="bg-black/50 border-green-500/30 text-green-400"
                        />
                      </div>
                    )}
                  </AccordionContent>
                </AccordionItem>

                {/* Privacy Settings */}
                <AccordionItem value="privacy" className="border-green-500/30">
                  <AccordionTrigger className="text-green-400 hover:text-green-300">
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4" />
                      Privacy
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">Incognito Mode</Label>
                      <Switch checked={settings.incognitoMode} onCheckedChange={(v) => setSettings(prev => ({ ...prev, incognitoMode: v }))} />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">Save History</Label>
                      <Switch checked={preferences.saveHistory} onCheckedChange={(v) => setPreferences(prev => ({ ...prev, saveHistory: v }))} />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label className="text-green-400 text-sm">Encrypt Files</Label>
                      <Switch checked={settings.encryptFiles} onCheckedChange={(v) => setSettings(prev => ({ ...prev, encryptFiles: v }))} />
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>
          </SheetContent>
        </Sheet>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-6">
          {/* Quick Setup Banner */}
          {!serverUrl && (
            <Alert className="border-yellow-500/50 bg-yellow-950/20 mb-6">
              <AlertCircle className="h-5 w-5 text-yellow-400" />
              <AlertTitle className="text-yellow-400">Server Not Configured</AlertTitle>
              <AlertDescription className="text-yellow-600">
                Click "Setup" button above to connect to your RS Downloader server
                <Button onClick={() => setShowServerConfig(true)} className="ml-4 bg-yellow-500 hover:bg-yellow-600 text-black" size="sm">
                  Setup Server
                </Button>
              </AlertDescription>
            </Alert>
          )}

          {/* Main Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="w-full grid grid-cols-6 lg:grid-cols-12 gap-1 bg-green-950/50 border border-green-500/30 p-1 h-auto">
              <TabsTrigger value="download" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <Download className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">Download</span>
              </TabsTrigger>
              <TabsTrigger value="batch" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <Layers className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">Batch</span>
              </TabsTrigger>
              <TabsTrigger value="queue" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <ListTodo className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">Queue</span>
              </TabsTrigger>
              <TabsTrigger value="history" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <History className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">History</span>
              </TabsTrigger>
              <TabsTrigger value="tools" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <Wand2 className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">Tools</span>
              </TabsTrigger>
              <TabsTrigger value="ai" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <Brain className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">AI</span>
              </TabsTrigger>
              <TabsTrigger value="cloud" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <Cloud className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">Cloud</span>
              </TabsTrigger>
              <TabsTrigger value="platforms" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <Globe className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">Platforms</span>
              </TabsTrigger>
              <TabsTrigger value="features" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <Zap className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">Features</span>
              </TabsTrigger>
              <TabsTrigger value="stats" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <BarChart3 className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">Stats</span>
              </TabsTrigger>
              <TabsTrigger value="schedule" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <Calendar className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">Schedule</span>
              </TabsTrigger>
              <TabsTrigger value="about" className="data-[state=active]:bg-green-500 data-[state=active]:text-black text-green-400 text-xs">
                <Info className="h-4 w-4 lg:mr-1" />
                <span className="hidden lg:inline">About</span>
              </TabsTrigger>
            </TabsList>

            {/* Download Tab */}
            <TabsContent value="download" className="mt-6 space-y-6">
              <div className="grid gap-6 lg:grid-cols-3">
                {/* Left Panel */}
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
                          className="flex-1 bg-black/50 border-green-500/30 text-green-400 placeholder:text-green-700 focus:border-green-500"
                        />
                        <Button onClick={fetchVideoInfo} disabled={loading || !serverUrl} className="bg-green-500 hover:bg-green-600 text-black font-semibold">
                          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
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
                            <img src={videoInfo.thumbnail} alt={videoInfo.title} className="w-full h-full object-cover rounded-t-lg md:rounded-l-lg md:rounded-tr-none" />
                            <Badge className="absolute bottom-2 right-2 bg-black/80 text-green-400 border-green-500/50">
                              {videoInfo.duration}
                            </Badge>
                          </div>
                          <div className="flex-1 p-4">
                            <h3 className="font-bold text-green-400 text-lg mb-2 line-clamp-2">{videoInfo.title}</h3>
                            <div className="space-y-1 text-sm text-green-600">
                              <p className="flex items-center gap-2"><Youtube className="h-4 w-4" />{videoInfo.channel}</p>
                              <p className="flex items-center gap-2"><Eye className="h-4 w-4" />{videoInfo.viewCount} views</p>
                            </div>
                            <Button variant="outline" size="sm" className="mt-3 border-green-500/50 text-green-400 hover:bg-green-500/10" onClick={() => copyToClipboard(videoInfo.id)}>
                              <Copy className="h-3 w-3 mr-1" />Copy ID
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
                            <Video className="h-4 w-4 mr-1" />Video
                          </TabsTrigger>
                          <TabsTrigger value="audio" className="data-[state=active]:bg-green-500 data-[state=active]:text-black">
                            <Music className="h-4 w-4 mr-1" />Audio
                          </TabsTrigger>
                          <TabsTrigger value="thumbnail" className="data-[state=active]:bg-green-500 data-[state=active]:text-black">
                            <Image className="h-4 w-4 mr-1" />Thumb
                          </TabsTrigger>
                          <TabsTrigger value="subtitle" className="data-[state=active]:bg-green-500 data-[state=active]:text-black">
                            <Subtitles className="h-4 w-4 mr-1" />Subs
                          </TabsTrigger>
                        </TabsList>
                      </CardHeader>

                      <CardContent className="pt-6">
                        {/* Video Tab */}
                        <TabsContent value="video" className="space-y-4 mt-0">
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label className="text-green-400">Quality</Label>
                              <Select value={settings.videoQuality} onValueChange={(v) => setSettings(prev => ({ ...prev, videoQuality: v }))}>
                                <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent className="bg-black border-green-500/30">
                                  {VIDEO_QUALITIES.map((q) => (
                                    <SelectItem key={q.value} value={q.value} className="hover:bg-green-500/10">
                                      {q.label}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="space-y-2">
                              <Label className="text-green-400">Format</Label>
                              <Select value={settings.videoFormat} onValueChange={(v) => setSettings(prev => ({ ...prev, videoFormat: v }))}>
                                <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent className="bg-black border-green-500/30">
                                  {VIDEO_FORMATS.map((f) => (
                                    <SelectItem key={f.value} value={f.value} className="hover:bg-green-500/10">
                                      {f.label}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                          </div>
                          <div className="flex gap-2 flex-wrap">
                            <div className="flex items-center gap-2">
                              <Checkbox id="hdr" checked={settings.hdrSupport} onCheckedChange={(v) => setSettings(prev => ({ ...prev, hdrSupport: !!v }))} />
                              <Label htmlFor="hdr" className="text-green-400 text-sm">HDR</Label>
                            </div>
                            <div className="flex items-center gap-2">
                              <Checkbox id="av1" checked={settings.av1Support} onCheckedChange={(v) => setSettings(prev => ({ ...prev, av1Support: !!v }))} />
                              <Label htmlFor="av1" className="text-green-400 text-sm">AV1</Label>
                            </div>
                          </div>
                          <Button onClick={() => startDownload("video")} disabled={downloading || !url || !serverUrl} className="w-full bg-green-500 hover:bg-green-600 text-black font-semibold h-12">
                            {downloading ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <Video className="h-5 w-5 mr-2" />}
                            Download Video
                          </Button>
                        </TabsContent>

                        {/* Audio Tab */}
                        <TabsContent value="audio" className="space-y-4 mt-0">
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label className="text-green-400">Quality</Label>
                              <Select value={settings.audioQuality} onValueChange={(v) => setSettings(prev => ({ ...prev, audioQuality: v }))}>
                                <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent className="bg-black border-green-500/30">
                                  {AUDIO_QUALITIES.map((q) => (
                                    <SelectItem key={q.value} value={q.value} className="hover:bg-green-500/10">
                                      {q.label}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="space-y-2">
                              <Label className="text-green-400">Format</Label>
                              <Select value={settings.audioFormat} onValueChange={(v) => setSettings(prev => ({ ...prev, audioFormat: v }))}>
                                <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent className="bg-black border-green-500/30">
                                  {AUDIO_FORMATS.map((f) => (
                                    <SelectItem key={f.value} value={f.value} className="hover:bg-green-500/10">
                                      {f.label}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                          </div>
                          <div className="flex gap-2 flex-wrap">
                            <div className="flex items-center gap-2">
                              <Checkbox id="thumb" checked={settings.embedThumbnail} onCheckedChange={(v) => setSettings(prev => ({ ...prev, embedThumbnail: !!v }))} />
                              <Label htmlFor="thumb" className="text-green-400 text-sm">Embed Thumbnail</Label>
                            </div>
                            <div className="flex items-center gap-2">
                              <Checkbox id="meta" checked={settings.embedMetadata} onCheckedChange={(v) => setSettings(prev => ({ ...prev, embedMetadata: !!v }))} />
                              <Label htmlFor="meta" className="text-green-400 text-sm">Metadata</Label>
                            </div>
                          </div>
                          <Button onClick={() => startDownload("audio")} disabled={downloading || !url || !serverUrl} className="w-full bg-green-500 hover:bg-green-600 text-black font-semibold h-12">
                            {downloading ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <Music className="h-5 w-5 mr-2" />}
                            Download Audio
                          </Button>
                        </TabsContent>

                        {/* Thumbnail Tab */}
                        <TabsContent value="thumbnail" className="space-y-4 mt-0">
                          <p className="text-green-600 text-sm">Download the video thumbnail in maximum available quality.</p>
                          <Button onClick={() => startDownload("thumbnail")} disabled={downloading || !url || !serverUrl} className="w-full bg-green-500 hover:bg-green-600 text-black font-semibold h-12">
                            {downloading ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <Image className="h-5 w-5 mr-2" />}
                            Download Thumbnail
                          </Button>
                        </TabsContent>

                        {/* Subtitle Tab */}
                        <TabsContent value="subtitle" className="space-y-4 mt-0">
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label className="text-green-400">Language</Label>
                              <Select value={settings.subtitleLang} onValueChange={(v) => setSettings(prev => ({ ...prev, subtitleLang: v }))}>
                                <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent className="bg-black border-green-500/30">
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
                            <div className="space-y-2">
                              <Label className="text-green-400">Format</Label>
                              <Select value={settings.subtitleFormat} onValueChange={(v) => setSettings(prev => ({ ...prev, subtitleFormat: v }))}>
                                <SelectTrigger className="bg-black/50 border-green-500/30 text-green-400">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent className="bg-black border-green-500/30">
                                  {SUBTITLE_FORMATS.map((f) => (
                                    <SelectItem key={f.value} value={f.value} className="hover:bg-green-500/10">
                                      {f.label}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                          </div>
                          <Button onClick={() => startDownload("subtitle")} disabled={downloading || !url || !serverUrl} className="w-full bg-green-500 hover:bg-green-600 text-black font-semibold h-12">
                            {downloading ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <Subtitles className="h-5 w-5 mr-2" />}
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
                          {downloadProgress.status === "complete" ? <CheckCircle2 className="h-4 w-4 text-green-400" /> : downloadProgress.status === "error" ? <AlertCircle className="h-4 w-4 text-red-400" /> : <Loader2 className="h-4 w-4 animate-spin" />}
                          {downloadProgress.status === "complete" ? "Download Complete" : downloadProgress.status === "error" ? "Download Failed" : "Downloading..."}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {downloadProgress.status !== "error" && (
                          <div className="space-y-2">
                            <Progress value={downloadProgress.progress} className="h-2 bg-green-950 [&>div]:bg-green-500" />
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

                {/* Right Panel */}
                <div className="space-y-6">
                  {/* Quick Stats */}
                  <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-green-400 text-lg flex items-center gap-2">
                        <Activity className="h-5 w-5" />
                        QUICK STATS
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-3 bg-green-950/30 rounded-lg">
                          <p className="text-2xl font-bold text-green-400">{downloadHistory.length}</p>
                          <p className="text-xs text-green-600">Downloads</p>
                        </div>
                        <div className="text-center p-3 bg-green-950/30 rounded-lg">
                          <p className="text-2xl font-bold text-green-400">{totalFeatures}</p>
                          <p className="text-xs text-green-600">Features</p>
                        </div>
                        <div className="text-center p-3 bg-green-950/30 rounded-lg">
                          <p className="text-2xl font-bold text-green-400">{PLATFORMS.length}</p>
                          <p className="text-xs text-green-600">Platforms</p>
                        </div>
                        <div className="text-center p-3 bg-green-950/30 rounded-lg">
                          <p className="text-2xl font-bold text-green-400">{downloadQueue.length}</p>
                          <p className="text-xs text-green-600">In Queue</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Supported Platforms Quick View */}
                  <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-green-400 text-lg flex items-center gap-2">
                        <Globe className="h-5 w-5" />
                        PLATFORMS
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-1">
                        {PLATFORMS.slice(0, 15).map((p, i) => (
                          <Tooltip key={i}>
                            <TooltipTrigger>
                              <Badge variant="outline" className="border-green-500/50 text-green-400 text-xs">
                                {p.name}
                              </Badge>
                            </TooltipTrigger>
                            <TooltipContent className="bg-black border-green-500/30">
                              <p className="text-green-400">{p.name}</p>
                              <p className="text-green-600 text-xs">Features: {p.features.length}</p>
                            </TooltipContent>
                          </Tooltip>
                        ))}
                        <Badge variant="outline" className="border-green-500/50 text-green-400 text-xs">
                          +{PLATFORMS.length - 15} more
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Author Card */}
                  <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                    <CardContent className="pt-6">
                      <div className="text-center space-y-3">
                        <div className={`flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20 border-2 border-green-500/50 mx-auto ${theme.glowEffects ? 'shadow-lg shadow-green-500/20' : ''}`}>
                          <Terminal className="h-8 w-8 text-green-400" />
                        </div>
                        <div>
                          <h3 className="font-bold text-green-400">RS (RAJSARASWATI JATAV)</h3>
                          <p className="text-xs text-green-600">LEGENDARY EXPERT</p>
                        </div>
                        <div className="flex justify-center gap-3">
                          <a href="https://youtube.com/@T3rmuxk1ng" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300">
                            <Youtube className="h-5 w-5" />
                          </a>
                          <a href="https://github.com/T3RMUXK1NG" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300">
                            <Github className="h-5 w-5" />
                          </a>
                        </div>
                        <p className="text-xs text-green-700">T3rmuxk1ng @ YouTube</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>

            {/* Batch Download Tab */}
            <TabsContent value="batch" className="mt-6 space-y-6">
              <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-green-400 flex items-center gap-2">
                    <Layers className="h-5 w-5" />
                    BATCH DOWNLOAD
                  </CardTitle>
                  <CardDescription className="text-green-600">
                    Download multiple URLs at once - one per line
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    placeholder="Paste multiple URLs here (one per line)&#10;https://youtube.com/watch?v=...&#10;https://youtube.com/watch?v=...&#10;https://youtube.com/watch?v=..."
                    className="min-h-40 bg-black/50 border-green-500/30 text-green-400 placeholder:text-green-700"
                    value={urls.join("\n")}
                    onChange={(e) => setUrls(e.target.value.split("\n").filter(u => u.trim()))}
                  />
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="border-green-500/50 text-green-400">
                      {urls.length} URLs
                    </Badge>
                    <div className="flex gap-2">
                      <Button variant="outline" onClick={() => setUrls([])} className="border-green-500/50 text-green-400">
                        <Trash2 className="h-4 w-4 mr-1" />Clear
                      </Button>
                      <Button disabled={urls.length === 0 || !serverUrl} className="bg-green-500 hover:bg-green-600 text-black">
                        <Download className="h-4 w-4 mr-1" />Start Batch
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Queue Tab */}
            <TabsContent value="queue" className="mt-6 space-y-6">
              <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-green-400 flex items-center gap-2">
                    <ListTodo className="h-5 w-5" />
                    DOWNLOAD QUEUE
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {downloadQueue.length === 0 ? (
                    <div className="text-center py-8 text-green-600">
                      <ListTodo className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>No downloads in queue</p>
                    </div>
                  ) : (
                    <ScrollArea className="h-64">
                      <div className="space-y-2">
                        {downloadQueue.map((item, i) => (
                          <div key={item.id} className="flex items-center justify-between p-2 bg-green-950/30 rounded-lg">
                            <div className="flex-1 truncate">
                              <p className="text-green-400 text-sm truncate">{item.title}</p>
                              <p className="text-green-600 text-xs">{item.type} • {item.quality}</p>
                            </div>
                            <Badge variant="outline" className="border-green-500/50 text-green-400 ml-2">
                              #{i + 1}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* History Tab */}
            <TabsContent value="history" className="mt-6 space-y-6">
              <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="text-green-400 flex items-center gap-2">
                    <History className="h-5 w-5" />
                    DOWNLOAD HISTORY
                  </CardTitle>
                  {downloadHistory.length > 0 && (
                    <Button variant="ghost" size="sm" onClick={() => setDownloadHistory([])} className="text-green-600 hover:text-green-400">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </CardHeader>
                <CardContent>
                  {downloadHistory.length === 0 ? (
                    <div className="text-center py-8 text-green-600">
                      <History className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>No download history</p>
                    </div>
                  ) : (
                    <ScrollArea className="h-64">
                      <div className="space-y-2">
                        {downloadHistory.map((item) => (
                          <div key={item.id} className="flex items-center justify-between p-2 bg-green-950/30 rounded-lg">
                            <div className="flex-1 truncate">
                              <p className="text-green-400 text-sm truncate">{item.title}</p>
                              <p className="text-green-600 text-xs">{item.type} • {item.quality}</p>
                            </div>
                            <div className="text-right">
                              <Badge variant="outline" className="border-green-500/50 text-green-400">
                                <CheckCircle2 className="h-3 w-3 mr-1" />Complete
                              </Badge>
                              <p className="text-green-600 text-xs mt-1">{item.timestamp.toLocaleTimeString()}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Tools Tab */}
            <TabsContent value="tools" className="mt-6 space-y-6">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {/* Video Tools */}
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-green-400 flex items-center gap-2 text-base">
                      <Video className="h-4 w-4" />
                      Video Tools
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-2">
                      {["Trim", "Merge", "Split", "Compress", "Convert", "Crop", "Rotate", "Watermark"].map((tool) => (
                        <Button key={tool} variant="outline" size="sm" className="border-green-500/50 text-green-400 text-xs">
                          {tool}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Audio Tools */}
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-green-400 flex items-center gap-2 text-base">
                      <Music className="h-4 w-4" />
                      Audio Tools
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-2">
                      {["Trim", "Merge", "Convert", "Normalize", "Speed", "Pitch", "Fade", "Enhance"].map((tool) => (
                        <Button key={tool} variant="outline" size="sm" className="border-green-500/50 text-green-400 text-xs">
                          {tool}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Image Tools */}
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-green-400 flex items-center gap-2 text-base">
                      <Image className="h-4 w-4" />
                      Image Tools
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-2">
                      {["Resize", "Crop", "Convert", "Compress", "Filter", "Watermark", "Rotate", "Collage"].map((tool) => (
                        <Button key={tool} variant="outline" size="sm" className="border-green-500/50 text-green-400 text-xs">
                          {tool}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* GIF Tools */}
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-green-400 flex items-center gap-2 text-base">
                      <FileImage className="h-4 w-4" />
                      GIF Tools
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-2">
                      {["Video to GIF", "GIF to Video", "Resize", "Optimize", "Reverse", "Crop", "Speed", "Merge"].map((tool) => (
                        <Button key={tool} variant="outline" size="sm" className="border-green-500/50 text-green-400 text-xs">
                          {tool}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Subtitle Tools */}
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-green-400 flex items-center gap-2 text-base">
                      <Subtitles className="h-4 w-4" />
                      Subtitle Tools
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-2">
                      {["Generate", "Translate", "Convert", "Sync", "Merge", "Edit", "Burn", "Extract"].map((tool) => (
                        <Button key={tool} variant="outline" size="sm" className="border-green-500/50 text-green-400 text-xs">
                          {tool}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Metadata Tools */}
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-green-400 flex items-center gap-2 text-base">
                      <FileText className="h-4 w-4" />
                      Metadata Tools
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-2">
                      {["View", "Edit", "Remove", "Embed", "Extract", "Copy", "Template", "Auto-fill"].map((tool) => (
                        <Button key={tool} variant="outline" size="sm" className="border-green-500/50 text-green-400 text-xs">
                          {tool}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* AI Tab */}
            <TabsContent value="ai" className="mt-6 space-y-6">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[
                  { name: "Smart Recommendations", icon: Sparkles, desc: "AI-powered content suggestions based on your history" },
                  { name: "Auto Subtitles", icon: Subtitles, desc: "Generate subtitles using AI speech recognition" },
                  { name: "Auto Translation", icon: Globe, desc: "Translate subtitles to any language" },
                  { name: "Content Summary", icon: FileText, desc: "AI-generated video summaries" },
                  { name: "Smart Filename", icon: File, desc: "Auto-generate descriptive filenames" },
                  { name: "Duplicate Detection", icon: Copy, desc: "Detect and remove duplicate content" },
                  { name: "Scene Detection", icon: Film, desc: "AI-powered scene detection" },
                  { name: "Object Detection", icon: Target, desc: "Detect objects in videos" },
                  { name: "Text Recognition", icon: FileText, desc: "OCR for images and videos" },
                  { name: "Thumbnail Generator", icon: Image, desc: "AI-powered thumbnail creation" },
                  { name: "Voice Enhancement", icon: Mic, desc: "AI voice enhancement" },
                  { name: "Video Upscaling", icon: Maximize, desc: "AI video upscaling" },
                ].map((feature) => (
                  <Card key={feature.name} className="border-green-500/30 bg-black/50 backdrop-blur-sm hover:border-green-500/50 transition-colors cursor-pointer">
                    <CardContent className="pt-6">
                      <div className="flex items-start gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/20">
                          <feature.icon className="h-5 w-5 text-green-400" />
                        </div>
                        <div>
                          <h3 className="font-medium text-green-400">{feature.name}</h3>
                          <p className="text-xs text-green-600 mt-1">{feature.desc}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Cloud Tab */}
            <TabsContent value="cloud" className="mt-6 space-y-6">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[
                  { name: "Google Drive", icon: Cloud, status: "available" },
                  { name: "Dropbox", icon: Cloud, status: "available" },
                  { name: "OneDrive", icon: Cloud, status: "available" },
                  { name: "iCloud", icon: Cloud, status: "coming" },
                  { name: "Mega", icon: Cloud, status: "available" },
                  { name: "pCloud", icon: Cloud, status: "coming" },
                  { name: "Box", icon: Cloud, status: "available" },
                  { name: "WebDAV", icon: Server, status: "available" },
                  { name: "FTP/SFTP", icon: HardDrive, status: "available" },
                ].map((cloud) => (
                  <Card key={cloud.name} className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <cloud.icon className="h-8 w-8 text-green-400" />
                          <div>
                            <h3 className="font-medium text-green-400">{cloud.name}</h3>
                            <p className="text-xs text-green-600">{cloud.status === "available" ? "Ready to connect" : "Coming soon"}</p>
                          </div>
                        </div>
                        <Button variant="outline" size="sm" className="border-green-500/50 text-green-400" disabled={cloud.status === "coming"}>
                          Connect
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Platforms Tab */}
            <TabsContent value="platforms" className="mt-6 space-y-6">
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                {PLATFORMS.map((platform, i) => (
                  <Card key={i} className="border-green-500/30 bg-black/50 backdrop-blur-sm hover:border-green-500/50 transition-colors">
                    <CardContent className="pt-4 pb-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg" style={{ backgroundColor: `${platform.color}20` }}>
                          <platform.icon className="h-5 w-5" style={{ color: platform.color }} />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-green-400">{platform.name}</h3>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {platform.features.slice(0, 3).map((f, j) => (
                              <Badge key={j} variant="outline" className="border-green-500/30 text-green-600 text-xs px-1">
                                {f}
                              </Badge>
                            ))}
                            {platform.features.length > 3 && (
                              <Badge variant="outline" className="border-green-500/30 text-green-600 text-xs px-1">
                                +{platform.features.length - 3}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Features Tab */}
            <TabsContent value="features" className="mt-6 space-y-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-green-400">{totalFeatures}+ Features Available</h2>
                <p className="text-green-600">Explore all the amazing features of RS Downloader</p>
              </div>
              
              <Accordion type="multiple" className="w-full space-y-2">
                {FEATURE_CATEGORIES.map((category, i) => (
                  <AccordionItem key={i} value={`category-${i}`} className="border-green-500/30 bg-black/50 rounded-lg px-4">
                    <AccordionTrigger className="text-green-400 hover:text-green-300">
                      <div className="flex items-center gap-3">
                        <category.icon className="h-5 w-5" />
                        <span>{category.category}</span>
                        <Badge variant="outline" className="border-green-500/50 text-green-400">
                          {category.features.length} features
                        </Badge>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3 pt-2">
                        {category.features.map((feature, j) => (
                          <div key={j} className="flex items-start gap-2 p-2 bg-green-950/30 rounded-lg">
                            <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0 mt-0.5" />
                            <div>
                              <p className="text-green-400 text-sm font-medium">{feature.name}</p>
                              <p className="text-green-600 text-xs">{feature.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </TabsContent>

            {/* Stats Tab */}
            <TabsContent value="stats" className="mt-6 space-y-6">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/20">
                        <Download className="h-6 w-6 text-green-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-green-400">{downloadHistory.length}</p>
                        <p className="text-sm text-green-600">Total Downloads</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/20">
                        <Zap className="h-6 w-6 text-green-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-green-400">{totalFeatures}</p>
                        <p className="text-sm text-green-600">Features</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/20">
                        <Globe className="h-6 w-6 text-green-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-green-400">{PLATFORMS.length}</p>
                        <p className="text-sm text-green-600">Platforms</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/20">
                        <Shield className="h-6 w-6 text-green-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-green-400">100%</p>
                        <p className="text-sm text-green-600">Secure</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Schedule Tab */}
            <TabsContent value="schedule" className="mt-6 space-y-6">
              <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-green-400 flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    SCHEDULED DOWNLOADS
                  </CardTitle>
                  <CardDescription className="text-green-600">
                    Schedule downloads for later
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label className="text-green-400">URL</Label>
                      <Input placeholder="Enter URL to schedule" className="bg-black/50 border-green-500/30 text-green-400" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-green-400">Schedule Time</Label>
                      <Input type="datetime-local" className="bg-black/50 border-green-500/30 text-green-400" />
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Checkbox id="recurring" />
                      <Label htmlFor="recurring" className="text-green-400 text-sm">Recurring</Label>
                    </div>
                    <Select defaultValue="daily">
                      <SelectTrigger className="w-32 bg-black/50 border-green-500/30 text-green-400">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-black border-green-500/30">
                        <SelectItem value="daily">Daily</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                        <SelectItem value="monthly">Monthly</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button className="bg-green-500 hover:bg-green-600 text-black">
                    <Calendar className="h-4 w-4 mr-2" />Schedule Download
                  </Button>
                  
                  {scheduledDownloads.length === 0 && (
                    <div className="text-center py-8 text-green-600">
                      <Calendar className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>No scheduled downloads</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* About Tab */}
            <TabsContent value="about" className="mt-6 space-y-6">
              <Card className="border-green-500/30 bg-black/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-green-400 flex items-center gap-2">
                    <Info className="h-5 w-5" />
                    ABOUT RS DOWNLOADER
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center py-4">
                    <div className={`flex h-20 w-20 items-center justify-center rounded-full bg-green-500/20 border-2 border-green-500/50 mx-auto mb-4 ${theme.glowEffects ? 'shadow-lg shadow-green-500/20' : ''}`}>
                      <Terminal className="h-10 w-10 text-green-400" />
                    </div>
                    <h2 className="text-2xl font-bold text-green-400">RS DOWNLOADER</h2>
                    <p className="text-green-600">v3.0.0 ULTIMATE NEXUS</p>
                    <Badge variant="outline" className="border-green-500/50 text-green-400 mt-2">
                      {totalFeatures}+ FEATURES
                    </Badge>
                  </div>
                  
                  <Separator className="bg-green-500/30" />
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-green-600">Platforms Supported</span>
                      <span className="text-green-400">{PLATFORMS.length}+</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-600">Video Formats</span>
                      <span className="text-green-400">{VIDEO_FORMATS.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-600">Audio Formats</span>
                      <span className="text-green-400">{AUDIO_FORMATS.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-600">Video Qualities</span>
                      <span className="text-green-400">{VIDEO_QUALITIES.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-600">Audio Qualities</span>
                      <span className="text-green-400">{AUDIO_QUALITIES.length}</span>
                    </div>
                  </div>
                  
                  <Separator className="bg-green-500/30" />
                  
                  <div className="text-center">
                    <h3 className="font-bold text-green-400 mb-2">Created by</h3>
                    <p className="text-lg text-green-400">RS (RAJSARASWATI JATAV)</p>
                    <p className="text-sm text-green-600">T3rmuxk1ng @ YouTube</p>
                    <div className="flex justify-center gap-4 mt-4">
                      <a href="https://youtube.com/@T3rmuxk1ng" target="_blank" rel="noopener noreferrer">
                        <Button variant="outline" className="border-green-500/50 text-green-400">
                          <Youtube className="h-4 w-4 mr-2" />YouTube
                        </Button>
                      </a>
                      <a href="https://github.com/T3RMUXK1NG" target="_blank" rel="noopener noreferrer">
                        <Button variant="outline" className="border-green-500/50 text-green-400">
                          <Github className="h-4 w-4 mr-2" />GitHub
                        </Button>
                      </a>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </main>

        {/* Footer */}
        <footer className="border-t border-green-500/30 py-6 mt-8">
          <div className="container mx-auto px-4 text-center text-green-600 text-sm">
            <p>Made with ❤️ by RS (T3rmuxk1ng)</p>
            <p className="text-xs mt-1">🔱 ULTIMATE NEXUS v3.0.0 🔱 | {totalFeatures}+ Features | {PLATFORMS.length}+ Platforms</p>
          </div>
        </footer>
      </div>
      
      <Toaster position="bottom-right" />
    </TooltipProvider>
  );
}
