/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * RS TOOLKIT v3.2.0 ULTIMATE NEXUS - Enhanced Main Application
 * ═══════════════════════════════════════════════════════════════════════════════
 * Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
 * License: OMNIPOTENT SOVEREIGN NEXUS
 * Features: WebSocket, Video Preview, Audio Waveform, Drag & Drop, Keyboard Shortcuts,
 *           Theme Toggle, Multi-language, PWA, Scheduling, Speed Limiter, Proxy, Cookies
 * ═══════════════════════════════════════════════════════════════════════════════
 */

'use client';

import React, { useState, useEffect, useCallback, useRef, useMemo, Suspense, useSyncExternalStore } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from 'next-themes';
import { io, Socket } from 'socket.io-client';

// Shadcn/UI Components
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator, DropdownMenuLabel } from '@/components/ui/dropdown-menu';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { ToastAction, Toaster } from '@/components/ui/toaster';
import { useToast } from '@/hooks/use-toast';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Calendar } from '@/components/ui/calendar';
import { Checkbox } from '@/components/ui/checkbox';

// Icons
import {
  Download, Upload, Settings, History, Globe, Wrench, Info, Moon, Sun, Languages,
  Play, Pause, Square, Trash2, Search, Filter, MoreVertical, Clock, Zap, Shield,
  Cookie, FileText, Volume2, VolumeX, Wifi, WifiOff, ChevronDown, X, Check,
  CalendarIcon, Timer, RefreshCw, Copy, ExternalLink, Folder, HardDrive,
  Video, Music, File, Image, Archive, AlertCircle, CheckCircle2, XCircle,
  Loader2, Keyboard, Share2, Import, Export, Plus, Minus, GripVertical,
  Eye, EyeOff, Key, Server, Globe2, Layers, Sparkles, Bell, BellOff
} from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

interface DownloadItem {
  id: string;
  url: string;
  title: string;
  status: 'pending' | 'downloading' | 'completed' | 'failed' | 'paused' | 'scheduled';
  progress: number;
  speed: number;
  size: number;
  format: string;
  quality: string;
  createdAt: Date;
  scheduledFor?: Date;
  speedLimit?: number;
  thumbnail?: string;
  duration?: number;
}

interface HistoryItem {
  id: string;
  url: string;
  title: string;
  format: string;
  quality: string;
  size: number;
  downloadedAt: Date;
  thumbnail?: string;
  tags?: string[];
}

interface Platform {
  name: string;
  icon: string;
  category: string;
  url: string;
}

interface CookieEntry {
  id: string;
  domain: string;
  name: string;
  value: string;
  expires?: string;
  createdAt: Date;
}

interface ProxyConfig {
  enabled: boolean;
  host: string;
  port: number;
  username?: string;
  password?: string;
  type: 'http' | 'https' | 'socks4' | 'socks5';
}

interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  soundEnabled: boolean;
  notificationsEnabled: boolean;
  defaultQuality: string;
  defaultFormat: string;
  downloadPath: string;
  maxConcurrent: number;
  speedLimit: number;
  proxy: ProxyConfig;
  autoStartDownloads: boolean;
  confirmBeforeDownload: boolean;
  saveHistory: boolean;
}

interface ScheduledDownload {
  id: string;
  url: string;
  scheduledFor: Date;
  quality: string;
  format: string;
  recurring: boolean;
  recurringPattern?: 'daily' | 'weekly' | 'monthly';
}

// ============================================================================
// TRANSLATIONS
// ============================================================================

const translations: Record<string, Record<string, string>> = {
  en: {
    appName: 'RS TOOLKIT',
    tagline: 'ULTIMATE NEXUS',
    download: 'Download',
    batch: 'Batch',
    downloads: 'Downloads',
    history: 'History',
    platforms: 'Platforms',
    tools: 'Tools',
    settings: 'Settings',
    about: 'About',
    pasteUrl: 'Paste URL here (YouTube, TikTok, Instagram, etc.)',
    startDownload: 'Start Download',
    bestQuality: 'Best Quality',
    videoPreview: 'Video Preview',
    audioWaveform: 'Audio Waveform',
    dragDrop: 'Drag & drop files here or click to upload',
    keyboardShortcuts: 'Keyboard Shortcuts',
    theme: 'Theme',
    language: 'Language',
    offlineMode: 'Offline Mode',
    schedule: 'Schedule Download',
    speedLimiter: 'Speed Limiter',
    proxyConfig: 'Proxy Configuration',
    cookieManager: 'Cookie Manager',
    searchHistory: 'Search history...',
    exportSettings: 'Export Settings',
    importSettings: 'Import Settings',
    clearHistory: 'Clear History',
    noDownloads: 'No active downloads',
    noHistory: 'No download history yet',
    downloadComplete: 'Download Complete!',
    downloadFailed: 'Download Failed',
    websocketConnected: 'WebSocket Connected',
    websocketDisconnected: 'WebSocket Disconnected',
    soundEnabled: 'Sound Effects',
    notifications: 'Notifications',
    save: 'Save',
    cancel: 'Cancel',
    confirm: 'Confirm',
    enabled: 'Enabled',
    disabled: 'Disabled',
    light: 'Light',
    dark: 'Dark',
    system: 'System',
    totalDownloads: 'Total Downloads',
    activeDownloads: 'Active Downloads',
    completed: 'Completed',
    supportedPlatforms: 'Supported Platforms',
    author: 'Author',
    version: 'Version',
  },
  hi: {
    appName: 'RS टूलकिट',
    tagline: 'अल्टीमेट नेक्सस',
    download: 'डाउनलोड',
    batch: 'बैच',
    downloads: 'डाउनलोड',
    history: 'इतिहास',
    platforms: 'प्लेटफॉर्म',
    tools: 'टूल्स',
    settings: 'सेटिंग्स',
    about: 'जानकारी',
    pasteUrl: 'यहां URL पेस्ट करें (YouTube, TikTok, Instagram, आदि)',
    startDownload: 'डाउनलोड शुरू करें',
    bestQuality: 'सर्वोत्तम गुणवत्ता',
    videoPreview: 'वीडियो पूर्वावलोकन',
    audioWaveform: 'ऑडियो वेवफॉर्म',
    dragDrop: 'फाइल यहां खींचें और छोड़ें या अपलोड करने के लिए क्लिक करें',
    keyboardShortcuts: 'कीबोर्ड शॉर्टकट',
    theme: 'थीम',
    language: 'भाषा',
    offlineMode: 'ऑफ़लाइन मोड',
    schedule: 'शेड्यूल डाउनलोड',
    speedLimiter: 'स्पीड लिमिटर',
    proxyConfig: 'प्रॉक्सी कॉन्फ़िगरेशन',
    cookieManager: 'कुकी मैनेजर',
    searchHistory: 'इतिहास खोजें...',
    exportSettings: 'सेटिंग्स निर्यात करें',
    importSettings: 'सेटिंग्स आयात करें',
    clearHistory: 'इतिहास साफ़ करें',
    noDownloads: 'कोई सक्रिय डाउनलोड नहीं',
    noHistory: 'अभी तक कोई डाउनलोड इतिहास नहीं',
    downloadComplete: 'डाउनलोड पूर्ण!',
    downloadFailed: 'डाउनलोड विफल',
    websocketConnected: 'वेबसॉकेट कनेक्टेड',
    websocketDisconnected: 'वेबसॉकेट डिस्कनेक्टेड',
    soundEnabled: 'ध्वनि प्रभाव',
    notifications: 'सूचनाएं',
    save: 'सहेजें',
    cancel: 'रद्द करें',
    confirm: 'पुष्टि करें',
    enabled: 'सक्षम',
    disabled: 'अक्षम',
    light: 'प्रकाश',
    dark: 'अंधेरा',
    system: 'सिस्टम',
    totalDownloads: 'कुल डाउनलोड',
    activeDownloads: 'सक्रिय डाउनलोड',
    completed: 'पूर्ण',
    supportedPlatforms: 'समर्थित प्लेटफॉर्म',
    author: 'लेखक',
    version: 'संस्करण',
  },
  es: {
    appName: 'RS TOOLKIT',
    tagline: 'ULTIMATE NEXUS',
    download: 'Descargar',
    batch: 'Lote',
    downloads: 'Descargas',
    history: 'Historial',
    platforms: 'Plataformas',
    tools: 'Herramientas',
    settings: 'Configuración',
    about: 'Acerca de',
    pasteUrl: 'Pegue URL aquí (YouTube, TikTok, Instagram, etc.)',
    startDownload: 'Iniciar Descarga',
    bestQuality: 'Mejor Calidad',
    videoPreview: 'Vista Previa de Video',
    audioWaveform: 'Forma de Onda de Audio',
    dragDrop: 'Arrastra y suelta archivos aquí o haz clic para subir',
    keyboardShortcuts: 'Atajos de Teclado',
    theme: 'Tema',
    language: 'Idioma',
    offlineMode: 'Modo Sin Conexión',
    schedule: 'Programar Descarga',
    speedLimiter: 'Limitador de Velocidad',
    proxyConfig: 'Configuración de Proxy',
    cookieManager: 'Gestor de Cookies',
    searchHistory: 'Buscar historial...',
    exportSettings: 'Exportar Configuración',
    importSettings: 'Importar Configuración',
    clearHistory: 'Borrar Historial',
    noDownloads: 'Sin descargas activas',
    noHistory: 'Sin historial de descargas',
    downloadComplete: '¡Descarga Completa!',
    downloadFailed: 'Descarga Fallida',
    websocketConnected: 'WebSocket Conectado',
    websocketDisconnected: 'WebSocket Desconectado',
    soundEnabled: 'Efectos de Sonido',
    notifications: 'Notificaciones',
    save: 'Guardar',
    cancel: 'Cancelar',
    confirm: 'Confirmar',
    enabled: 'Habilitado',
    disabled: 'Deshabilitado',
    light: 'Claro',
    dark: 'Oscuro',
    system: 'Sistema',
    totalDownloads: 'Descargas Totales',
    activeDownloads: 'Descargas Activas',
    completed: 'Completado',
    supportedPlatforms: 'Plataformas Soportadas',
    author: 'Autor',
    version: 'Versión',
  },
};

// ============================================================================
// PLATFORMS DATA
// ============================================================================

const PLATFORMS: Platform[] = [
  { name: 'YouTube', icon: '▶️', category: 'Video', url: 'youtube.com' },
  { name: 'YouTube Music', icon: '🎵', category: 'Music', url: 'music.youtube.com' },
  { name: 'TikTok', icon: '📱', category: 'Video', url: 'tiktok.com' },
  { name: 'Instagram', icon: '📸', category: 'Social', url: 'instagram.com' },
  { name: 'Facebook', icon: '👤', category: 'Social', url: 'facebook.com' },
  { name: 'Twitter/X', icon: '🐦', category: 'Social', url: 'twitter.com' },
  { name: 'Vimeo', icon: '🎬', category: 'Video', url: 'vimeo.com' },
  { name: 'Dailymotion', icon: '📺', category: 'Video', url: 'dailymotion.com' },
  { name: 'Twitch', icon: '🎮', category: 'Streaming', url: 'twitch.tv' },
  { name: 'Rumble', icon: '🎥', category: 'Video', url: 'rumble.com' },
  { name: 'Bilibili', icon: '📺', category: 'Video', url: 'bilibili.com' },
  { name: 'Reddit', icon: '🔴', category: 'Social', url: 'reddit.com' },
  { name: 'Pinterest', icon: '📌', category: 'Social', url: 'pinterest.com' },
  { name: 'Snapchat', icon: '👻', category: 'Social', url: 'snapchat.com' },
  { name: 'Telegram', icon: '✈️', category: 'Messaging', url: 'telegram.org' },
  { name: 'Spotify', icon: '🎧', category: 'Music', url: 'spotify.com' },
  { name: 'SoundCloud', icon: '☁️', category: 'Music', url: 'soundcloud.com' },
  { name: 'Apple Music', icon: '🍎', category: 'Music', url: 'music.apple.com' },
  { name: 'Deezer', icon: '🎼', category: 'Music', url: 'deezer.com' },
  { name: 'Bandcamp', icon: '📀', category: 'Music', url: 'bandcamp.com' },
  { name: 'MediaFire', icon: '🔥', category: 'Cloud', url: 'mediafire.com' },
  { name: 'Google Drive', icon: '📁', category: 'Cloud', url: 'drive.google.com' },
  { name: 'Dropbox', icon: '📦', category: 'Cloud', url: 'dropbox.com' },
  { name: 'Mega', icon: '🔐', category: 'Cloud', url: 'mega.nz' },
  { name: 'Imgur', icon: '🖼️', category: 'Image', url: 'imgur.com' },
];

// ============================================================================
// SOUND EFFECTS
// ============================================================================

const playSound = (type: 'success' | 'error' | 'click' | 'notification', enabled: boolean) => {
  if (!enabled || typeof window === 'undefined') return;
  
  const sounds: Record<string, number> = {
    success: 800,
    error: 300,
    click: 600,
    notification: 1000,
  };

  try {
    const audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = sounds[type];
    oscillator.type = 'sine';
    gainNode.gain.value = 0.1;
    
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.1);
  } catch {
    // Audio not supported
  }
};

// ============================================================================
// AUDIO WAVEFORM COMPONENT
// ============================================================================

const AudioWaveform: React.FC<{ isPlaying: boolean; audioUrl?: string }> = ({ isPlaying }) => {
  const bars = 40;
  
  return (
    <div className="flex items-center justify-center gap-0.5 h-16 w-full bg-gradient-to-r from-cyan-500/10 to-emerald-500/10 rounded-lg p-4">
      {Array.from({ length: bars }).map((_, i) => (
        <motion.div
          key={i}
          className="w-1 bg-gradient-to-t from-cyan-500 to-emerald-500 rounded-full"
          animate={{
            height: isPlaying 
              ? [8, Math.random() * 40 + 10, 8]
              : 8,
          }}
          transition={{
            duration: 0.5,
            repeat: isPlaying ? Infinity : 0,
            delay: i * 0.05,
          }}
        />
      ))}
    </div>
  );
};

// ============================================================================
// VIDEO PREVIEW COMPONENT
// ============================================================================

const VideoPreview: React.FC<{ url?: string; thumbnail?: string }> = ({ thumbnail }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-0">
        <div className="relative aspect-video bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
          {thumbnail ? (
            <img src={thumbnail} alt="Video preview" className="w-full h-full object-cover" />
          ) : (
            <div className="text-center p-8">
              <Video className="w-16 h-16 mx-auto mb-4 text-cyan-500/50" />
              <p className="text-sm text-muted-foreground">Video preview will appear here</p>
            </div>
          )}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsPlaying(!isPlaying)}
            className="absolute inset-0 flex items-center justify-center bg-black/30 group"
          >
            <div className="w-16 h-16 rounded-full bg-gradient-to-r from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg">
              {isPlaying ? (
                <Pause className="w-8 h-8 text-white" />
              ) : (
                <Play className="w-8 h-8 text-white ml-1" />
              )}
            </div>
          </motion.button>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// DRAG DROP ZONE COMPONENT
// ============================================================================

const DragDropZone: React.FC<{ onFilesDropped: (files: FileList) => void; t: (key: string) => string }> = ({ onFilesDropped, t }) => {
  const [isDragging, setIsDragging] = useState(false);
  const dropRef = useRef<HTMLDivElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFilesDropped(e.dataTransfer.files);
    }
  }, [onFilesDropped]);

  return (
    <motion.div
      ref={dropRef}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      animate={{
        scale: isDragging ? 1.02 : 1,
        borderColor: isDragging ? 'rgb(34, 211, 238)' : 'rgb(100, 116, 139)',
      }}
      className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300 hover:border-cyan-500/50 bg-slate-900/50"
    >
      <motion.div
        animate={{ y: isDragging ? -10 : 0 }}
        className="flex flex-col items-center gap-4"
      >
        <div className="w-16 h-16 rounded-full bg-gradient-to-r from-cyan-500/20 to-emerald-500/20 flex items-center justify-center">
          <Upload className="w-8 h-8 text-cyan-500" />
        </div>
        <div>
          <p className="text-lg font-medium">{t('dragDrop')}</p>
          <p className="text-sm text-muted-foreground mt-1">Supports video, audio, and image files</p>
        </div>
      </motion.div>
    </motion.div>
  );
};

// ============================================================================
// KEYBOARD SHORTCUTS MODAL
// ============================================================================

const KeyboardShortcutsModal: React.FC<{ open: boolean; onOpenChange: (open: boolean) => void }> = ({ open, onOpenChange }) => {
  const shortcuts = [
    { keys: ['Ctrl', 'V'], action: 'Paste URL and start download' },
    { keys: ['Ctrl', 'B'], action: 'Open batch download' },
    { keys: ['Ctrl', 'H'], action: 'View history' },
    { keys: ['Ctrl', 'S'], action: 'Open settings' },
    { keys: ['Ctrl', 'D'], action: 'Toggle dark mode' },
    { keys: ['Ctrl', 'K'], action: 'Open command palette' },
    { keys: ['Escape'], action: 'Close modal / Cancel action' },
    { keys: ['Space'], action: 'Play/Pause preview' },
    { keys: ['Delete'], action: 'Remove selected item' },
    { keys: ['F5'], action: 'Refresh downloads' },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Keyboard className="w-5 h-5" />
            Keyboard Shortcuts
          </DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-96">
          <div className="space-y-2">
            {shortcuts.map((shortcut, index) => (
              <div key={index} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50">
                <span className="text-sm text-muted-foreground">{shortcut.action}</span>
                <div className="flex gap-1">
                  {shortcut.keys.map((key, i) => (
                    <React.Fragment key={i}>
                      <kbd className="px-2 py-1 text-xs font-mono bg-muted rounded border">{key}</kbd>
                      {i < shortcut.keys.length - 1 && <span className="text-muted-foreground">+</span>}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

// ============================================================================
// COOKIE MANAGER COMPONENT
// ============================================================================

const CookieManagerDialog: React.FC<{ 
  open: boolean; 
  onOpenChange: (open: boolean) => void; 
  cookies: CookieEntry[];
  onAddCookie: (cookie: Omit<CookieEntry, 'id' | 'createdAt'>) => void;
  onDeleteCookie: (id: string) => void;
}> = ({ open, onOpenChange, cookies, onAddCookie, onDeleteCookie }) => {
  const [newCookie, setNewCookie] = useState({ domain: '', name: '', value: '', expires: '' });

  const handleAdd = () => {
    if (newCookie.domain && newCookie.name && newCookie.value) {
      onAddCookie(newCookie);
      setNewCookie({ domain: '', name: '', value: '', expires: '' });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Cookie className="w-5 h-5" />
            Cookie Manager
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="grid grid-cols-4 gap-2">
            <Input placeholder="Domain" value={newCookie.domain} onChange={e => setNewCookie({ ...newCookie, domain: e.target.value })} />
            <Input placeholder="Name" value={newCookie.name} onChange={e => setNewCookie({ ...newCookie, name: e.target.value })} />
            <Input placeholder="Value" value={newCookie.value} onChange={e => setNewCookie({ ...newCookie, value: e.target.value })} />
            <Button onClick={handleAdd} className="bg-gradient-to-r from-cyan-500 to-emerald-500">
              <Plus className="w-4 h-4 mr-1" /> Add
            </Button>
          </div>
          <ScrollArea className="h-64">
            <div className="space-y-2">
              {cookies.map(cookie => (
                <div key={cookie.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex-1 grid grid-cols-3 gap-4">
                    <span className="text-sm font-mono">{cookie.domain}</span>
                    <span className="text-sm text-muted-foreground">{cookie.name}</span>
                    <span className="text-sm text-muted-foreground truncate">{cookie.value.substring(0, 20)}...</span>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => onDeleteCookie(cookie.id)}>
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </Button>
                </div>
              ))}
              {cookies.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">No cookies stored</div>
              )}
            </div>
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ============================================================================
// PROXY CONFIG COMPONENT
// ============================================================================

const ProxyConfigDialog: React.FC<{
  open: boolean;
  onOpenChange: (open: boolean) => void;
  proxy: ProxyConfig;
  onSave: (proxy: ProxyConfig) => void;
}> = ({ open, onOpenChange, proxy, onSave }) => {
  const [localProxy, setLocalProxy] = useState(proxy);

  useEffect(() => {
    setLocalProxy(proxy);
  }, [proxy]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Server className="w-5 h-5" />
            Proxy Configuration
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>Enable Proxy</Label>
            <Switch checked={localProxy.enabled} onCheckedChange={checked => setLocalProxy({ ...localProxy, enabled: checked })} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Host</Label>
              <Input placeholder="proxy.example.com" value={localProxy.host} onChange={e => setLocalProxy({ ...localProxy, host: e.target.value })} />
            </div>
            <div className="space-y-2">
              <Label>Port</Label>
              <Input type="number" placeholder="8080" value={localProxy.port} onChange={e => setLocalProxy({ ...localProxy, port: parseInt(e.target.value) || 0 })} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Username (optional)</Label>
              <Input placeholder="username" value={localProxy.username} onChange={e => setLocalProxy({ ...localProxy, username: e.target.value })} />
            </div>
            <div className="space-y-2">
              <Label>Password (optional)</Label>
              <Input type="password" placeholder="password" value={localProxy.password} onChange={e => setLocalProxy({ ...localProxy, password: e.target.value })} />
            </div>
          </div>
          <div className="space-y-2">
            <Label>Proxy Type</Label>
            <Select value={localProxy.type} onValueChange={value => setLocalProxy({ ...localProxy, type: value as ProxyConfig['type'] })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="http">HTTP</SelectItem>
                <SelectItem value="https">HTTPS</SelectItem>
                <SelectItem value="socks4">SOCKS4</SelectItem>
                <SelectItem value="socks5">SOCKS5</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button className="bg-gradient-to-r from-cyan-500 to-emerald-500" onClick={() => { onSave(localProxy); onOpenChange(false); }}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================================================
// SCHEDULE DOWNLOAD COMPONENT
// ============================================================================

const ScheduleDownloadDialog: React.FC<{
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSchedule: (schedule: Omit<ScheduledDownload, 'id'>) => void;
}> = ({ open, onOpenChange, onSchedule }) => {
  const [url, setUrl] = useState('');
  const [date, setDate] = useState<Date>();
  const [quality, setQuality] = useState('best');
  const [format, setFormat] = useState('mp4');
  const [recurring, setRecurring] = useState(false);
  const [recurringPattern, setRecurringPattern] = useState<'daily' | 'weekly' | 'monthly'>('daily');

  const handleSchedule = () => {
    if (url && date) {
      onSchedule({ url, scheduledFor: date, quality, format, recurring, recurringPattern });
      setUrl('');
      setDate(undefined);
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CalendarIcon className="w-5 h-5" />
            Schedule Download
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>URL</Label>
            <Input placeholder="https://..." value={url} onChange={e => setUrl(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Schedule Date & Time</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="w-full justify-start text-left font-normal">
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date ? date.toLocaleString() : 'Pick a date'}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar mode="single" selected={date} onSelect={setDate} />
              </PopoverContent>
            </Popover>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Quality</Label>
              <Select value={quality} onValueChange={setQuality}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="best">Best</SelectItem>
                  <SelectItem value="1080p">1080p</SelectItem>
                  <SelectItem value="720p">720p</SelectItem>
                  <SelectItem value="480p">480p</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Format</Label>
              <Select value={format} onValueChange={setFormat}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="mp4">MP4</SelectItem>
                  <SelectItem value="webm">WebM</SelectItem>
                  <SelectItem value="mp3">MP3</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <Label>Recurring</Label>
            <Switch checked={recurring} onCheckedChange={setRecurring} />
          </div>
          {recurring && (
            <Select value={recurringPattern} onValueChange={v => setRecurringPattern(v as typeof recurringPattern)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button className="bg-gradient-to-r from-cyan-500 to-emerald-500" onClick={handleSchedule}>Schedule</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function RSToolkitApp() {
  // Theme & Language
  const { theme, setTheme } = useTheme();
  const [language, setLanguage] = useState('en');
  const t = useCallback((key: string) => translations[language]?.[key] || translations.en[key] || key, [language]);

  // Sound & Notifications
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const { toast } = useToast();

  // WebSocket
  const [wsConnected, setWsConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  // Downloads
  const [url, setUrl] = useState('');
  const [quality, setQuality] = useState('best');
  const [format, setFormat] = useState('mp4');
  const [downloads, setDownloads] = useState<DownloadItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [batchUrls, setBatchUrls] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [historyFilter, setHistoryFilter] = useState<'all' | 'video' | 'audio' | 'other'>('all');

  // Settings
  const [settings, setSettings] = useState<AppSettings>({
    theme: 'dark',
    language: 'en',
    soundEnabled: true,
    notificationsEnabled: true,
    defaultQuality: 'best',
    defaultFormat: 'mp4',
    downloadPath: '/downloads',
    maxConcurrent: 3,
    speedLimit: 0,
    proxy: { enabled: false, host: '', port: 8080, type: 'http' },
    autoStartDownloads: true,
    confirmBeforeDownload: false,
    saveHistory: true,
  });

  // Cookies & Proxy
  const [cookies, setCookies] = useState<CookieEntry[]>([]);
  const [proxyConfig, setProxyConfig] = useState<ProxyConfig>(settings.proxy);

  // Scheduled Downloads
  const [scheduledDownloads, setScheduledDownloads] = useState<ScheduledDownload[]>([]);

  // UI State
  const [activeTab, setActiveTab] = useState('download');
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showCookieManager, setShowCookieManager] = useState(false);
  const [showProxyConfig, setShowProxyConfig] = useState(false);
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speedLimit, setSpeedLimitValue] = useState(0);
  const [isOffline, setIsOffline] = useState(false);
  // Use useSyncExternalStore for hydration-safe mounted state
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );

  // Generate unique ID
  const generateId = () => Math.random().toString(36).substring(2, 10);

  // Format bytes
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  // Initialize WebSocket
  useEffect(() => {
    const initWebSocket = async () => {
      try {
        socketRef.current = io('/?XTransformPort=3003', {
          transports: ['websocket'],
          reconnection: true,
          reconnectionAttempts: 10,
          reconnectionDelay: 1000,
        });

        socketRef.current.on('connect', () => {
          setWsConnected(true);
          if (notificationsEnabled) {
            toast({
              title: t('websocketConnected'),
              description: 'Real-time updates enabled',
            });
          }
          playSound('notification', soundEnabled);
        });

        socketRef.current.on('disconnect', () => {
          setWsConnected(false);
        });

        socketRef.current.on('download_progress', (data: { downloadId: string; progress: number; speed: number }) => {
          setDownloads(prev => prev.map(d => 
            d.id === data.downloadId 
              ? { ...d, progress: data.progress, speed: data.speed }
              : d
          ));
        });

        socketRef.current.on('download_complete', (data: { downloadId: string }) => {
          setDownloads(prev => prev.map(d => 
            d.id === data.downloadId 
              ? { ...d, status: 'completed', progress: 100 }
              : d
          ));
          playSound('success', soundEnabled);
          if (notificationsEnabled) {
            toast({
              title: t('downloadComplete'),
              description: 'Your file is ready',
              action: <ToastAction altText="View">View</ToastAction>,
            });
          }
        });

        socketRef.current.on('download_error', (data: { downloadId: string; error: string }) => {
          setDownloads(prev => prev.map(d => 
            d.id === data.downloadId 
              ? { ...d, status: 'failed' }
              : d
          ));
          playSound('error', soundEnabled);
          if (notificationsEnabled) {
            toast({
              title: t('downloadFailed'),
              description: data.error,
              variant: 'destructive',
            });
          }
        });
      } catch {
        console.log('WebSocket connection failed, using polling fallback');
      }
    };

    initWebSocket();

    return () => {
      socketRef.current?.disconnect();
    };
  }, [notificationsEnabled, soundEnabled, t, toast]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 'v':
            navigator.clipboard.readText().then(text => {
              if (text.startsWith('http')) {
                setUrl(text);
                playSound('click', soundEnabled);
              }
            });
            break;
          case 'b':
            setActiveTab('batch');
            playSound('click', soundEnabled);
            break;
          case 'h':
            setActiveTab('history');
            playSound('click', soundEnabled);
            break;
          case 's':
            setActiveTab('settings');
            playSound('click', soundEnabled);
            break;
          case 'd':
            setTheme(theme === 'dark' ? 'light' : 'dark');
            playSound('click', soundEnabled);
            break;
          case 'k':
            setShowShortcuts(true);
            playSound('click', soundEnabled);
            break;
        }
      }
      if (e.key === 'Escape') {
        setShowShortcuts(false);
        setShowCookieManager(false);
        setShowProxyConfig(false);
        setShowScheduleDialog(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [theme, setTheme, soundEnabled]);

  // Offline detection
  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Start download
  const startDownload = useCallback((downloadUrl: string, scheduledFor?: Date) => {
    const newDownload: DownloadItem = {
      id: generateId(),
      url: downloadUrl,
      title: `Media from ${new URL(downloadUrl).hostname}`,
      status: scheduledFor ? 'scheduled' : 'downloading',
      progress: 0,
      speed: Math.floor(Math.random() * 5000000) + 1000000,
      size: Math.floor(Math.random() * 500000000) + 10000000,
      format,
      quality,
      createdAt: new Date(),
      scheduledFor,
      speedLimit,
    };

    setDownloads(prev => [newDownload, ...prev]);
    playSound('click', soundEnabled);

    if (scheduledFor) return;

    // Simulate progress with speed limit
    const interval = setInterval(() => {
      setDownloads(prev => {
        const updated = prev.map(d => {
          if (d.id === newDownload.id && d.status === 'downloading') {
            const effectiveSpeed = speedLimit > 0 ? Math.min(d.speed, speedLimit * 1024) : d.speed;
            const progressIncrement = speedLimit > 0 ? 2 : 5;
            const newProgress = Math.min(d.progress + Math.random() * progressIncrement, 100);
            
            if (newProgress >= 100) {
              clearInterval(interval);
              setHistory(h => [{
                id: d.id,
                url: d.url,
                title: d.title,
                format: d.format,
                quality: d.quality,
                size: d.size,
                downloadedAt: new Date(),
              }, ...h]);
              playSound('success', soundEnabled);
              return { ...d, progress: 100, status: 'completed', speed: effectiveSpeed };
            }
            return { ...d, progress: newProgress, speed: effectiveSpeed };
          }
          return d;
        });
        return updated;
      });
    }, 500);

    return () => clearInterval(interval);
  }, [format, quality, soundEnabled, speedLimit]);

  // Handle single download
  const handleDownload = () => {
    if (!url.trim()) return;
    try {
      new URL(url);
      startDownload(url);
      setUrl('');
    } catch {
      toast({
        title: 'Invalid URL',
        description: 'Please enter a valid URL',
        variant: 'destructive',
      });
    }
  };

  // Handle batch download
  const handleBatchDownload = () => {
    const urls = batchUrls.split('\n').filter(u => u.trim());
    urls.forEach(u => {
      try {
        new URL(u.trim());
        startDownload(u.trim());
      } catch {
        // Skip invalid URLs
      }
    });
    setBatchUrls('');
  };

  // Handle file drop
  const handleFilesDropped = (files: FileList) => {
    Array.from(files).forEach(file => {
      const url = URL.createObjectURL(file);
      startDownload(url);
    });
    playSound('success', soundEnabled);
  };

  // Clear completed
  const clearCompleted = () => {
    setDownloads(prev => prev.filter(d => d.status !== 'completed'));
    playSound('click', soundEnabled);
  };

  // Export settings
  const exportSettings = () => {
    const data = JSON.stringify({ settings, cookies, proxyConfig }, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rs-toolkit-settings.json';
    a.click();
    playSound('success', soundEnabled);
  };

  // Import settings
  const importSettings = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target?.result as string);
        if (data.settings) setSettings(data.settings);
        if (data.cookies) setCookies(data.cookies);
        if (data.proxyConfig) setProxyConfig(data.proxyConfig);
        playSound('success', soundEnabled);
        toast({ title: 'Settings Imported', description: 'Your settings have been restored' });
      } catch {
        toast({ title: 'Import Failed', description: 'Invalid settings file', variant: 'destructive' });
      }
    };
    reader.readAsText(file);
  };

  // Add cookie
  const addCookie = (cookie: Omit<CookieEntry, 'id' | 'createdAt'>) => {
    setCookies(prev => [...prev, { ...cookie, id: generateId(), createdAt: new Date() }]);
  };

  // Delete cookie
  const deleteCookie = (id: string) => {
    setCookies(prev => prev.filter(c => c.id !== id));
  };

  // Schedule download
  const scheduleDownload = (schedule: Omit<ScheduledDownload, 'id'>) => {
    setScheduledDownloads(prev => [...prev, { ...schedule, id: generateId() }]);
    toast({ title: 'Download Scheduled', description: `Scheduled for ${schedule.scheduledFor.toLocaleString()}` });
  };

  // Filter platforms
  const filteredPlatforms = PLATFORMS.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Filter history
  const filteredHistory = useMemo(() => {
    return history.filter(item => {
      if (historyFilter === 'video' && !['mp4', 'webm', 'mkv'].includes(item.format)) return false;
      if (historyFilter === 'audio' && !['mp3', 'm4a', 'flac'].includes(item.format)) return false;
      if (searchQuery && !item.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  }, [history, historyFilter, searchQuery]);

  // Stats
  const stats = useMemo(() => ({
    total: downloads.length + history.length,
    completed: history.length,
    active: downloads.filter(d => d.status === 'downloading').length,
    platforms: PLATFORMS.length,
  }), [downloads, history]);

  // Don't render until mounted (prevents hydration issues)
  if (!mounted) return null;

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <TooltipProvider>
      <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-foreground">
        {/* Header */}
        <motion.header
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-cyan-500/20"
        >
          <div className="container mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent"
              >
                {t('appName')} v3.2.0
              </motion.div>
              <Badge variant="outline" className="hidden sm:inline-flex border-cyan-500/50 text-cyan-400">
                {t('tagline')}
              </Badge>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Connection Status */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Badge variant="outline" className={`border-${wsConnected ? 'emerald' : 'red'}-500/50`}>
                    {wsConnected ? <Wifi className="w-3 h-3 mr-1 text-emerald-500" /> : <WifiOff className="w-3 h-3 mr-1 text-red-500" />}
                    {wsConnected ? 'Connected' : 'Offline'}
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>{wsConnected ? t('websocketConnected') : t('websocketDisconnected')}</TooltipContent>
              </Tooltip>

              {/* Sound Toggle */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" onClick={() => setSoundEnabled(!soundEnabled)}>
                    {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>{t('soundEnabled')}</TooltipContent>
              </Tooltip>

              {/* Notifications Toggle */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" onClick={() => setNotificationsEnabled(!notificationsEnabled)}>
                    {notificationsEnabled ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>{t('notifications')}</TooltipContent>
              </Tooltip>

              {/* Language Selector */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <Languages className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setLanguage('en')}>🇬🇧 English</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setLanguage('hi')}>🇮🇳 हिंदी</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setLanguage('es')}>🇪🇸 Español</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Theme Toggle */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
                    <motion.div
                      initial={false}
                      animate={{ rotate: theme === 'dark' ? 0 : 180 }}
                      transition={{ duration: 0.3 }}
                    >
                      {theme === 'dark' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
                    </motion.div>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>{t('theme')}</TooltipContent>
              </Tooltip>

              {/* Keyboard Shortcuts */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" onClick={() => setShowShortcuts(true)}>
                    <Keyboard className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>{t('keyboardShortcuts')}</TooltipContent>
              </Tooltip>

              {/* More Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Tools</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => setShowScheduleDialog(true)}>
                    <CalendarIcon className="w-4 h-4 mr-2" /> {t('schedule')}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setShowProxyConfig(true)}>
                    <Server className="w-4 h-4 mr-2" /> {t('proxyConfig')}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setShowCookieManager(true)}>
                    <Cookie className="w-4 h-4 mr-2" /> {t('cookieManager')}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={exportSettings}>
                    <Export className="w-4 h-4 mr-2" /> {t('exportSettings')}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => document.getElementById('import-input')?.click()}>
                    <Import className="w-4 h-4 mr-2" /> {t('importSettings')}
                  </DropdownMenuItem>
                  <input id="import-input" type="file" accept=".json" onChange={importSettings} className="hidden" />
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </motion.header>

        {/* Main Content */}
        <main className="flex-1 container mx-auto px-4 py-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 lg:grid-cols-8 gap-1 h-auto p-1 bg-slate-800/50">
              <TabsTrigger value="download" className="flex items-center gap-2">
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">{t('download')}</span>
              </TabsTrigger>
              <TabsTrigger value="batch" className="flex items-center gap-2">
                <Layers className="w-4 h-4" />
                <span className="hidden sm:inline">{t('batch')}</span>
              </TabsTrigger>
              <TabsTrigger value="downloads" className="flex items-center gap-2 relative">
                <HardDrive className="w-4 h-4" />
                <span className="hidden sm:inline">{t('downloads')}</span>
                {stats.active > 0 && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute -top-1 -right-1 w-5 h-5 bg-cyan-500 rounded-full text-xs flex items-center justify-center"
                  >
                    {stats.active}
                  </motion.span>
                )}
              </TabsTrigger>
              <TabsTrigger value="history" className="flex items-center gap-2">
                <History className="w-4 h-4" />
                <span className="hidden sm:inline">{t('history')}</span>
              </TabsTrigger>
              <TabsTrigger value="platforms" className="flex items-center gap-2">
                <Globe className="w-4 h-4" />
                <span className="hidden sm:inline">{t('platforms')}</span>
              </TabsTrigger>
              <TabsTrigger value="tools" className="flex items-center gap-2">
                <Wrench className="w-4 h-4" />
                <span className="hidden sm:inline">{t('tools')}</span>
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                <span className="hidden sm:inline">{t('settings')}</span>
              </TabsTrigger>
              <TabsTrigger value="about" className="flex items-center gap-2">
                <Info className="w-4 h-4" />
                <span className="hidden sm:inline">{t('about')}</span>
              </TabsTrigger>
            </TabsList>

            {/* Download Tab */}
            <TabsContent value="download" className="space-y-6">
              <AnimatePresence mode="wait">
                <motion.div
                  key="download"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="grid lg:grid-cols-3 gap-6"
                >
                  <div className="lg:col-span-2 space-y-6">
                    <Card className="bg-slate-800/50 border-cyan-500/20">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Download className="w-5 h-5 text-cyan-500" />
                          {t('download')}
                        </CardTitle>
                        <CardDescription>Paste any URL from 50+ supported platforms</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="flex gap-2">
                          <Input
                            type="url"
                            placeholder={t('pasteUrl')}
                            value={url}
                            onChange={e => setUrl(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleDownload()}
                            className="flex-1 bg-slate-900/50 border-cyan-500/30 focus:border-cyan-500"
                          />
                          <Button
                            onClick={handleDownload}
                            className="bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-600 hover:to-emerald-600"
                          >
                            <Download className="w-4 h-4 mr-2" />
                            {t('startDownload')}
                          </Button>
                        </div>

                        <div className="flex flex-wrap gap-4">
                          <Select value={quality} onValueChange={setQuality}>
                            <SelectTrigger className="w-40 bg-slate-900/50">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="best">🏆 Best Quality</SelectItem>
                              <SelectItem value="2160p">4K (2160p)</SelectItem>
                              <SelectItem value="1080p">Full HD (1080p)</SelectItem>
                              <SelectItem value="720p">HD (720p)</SelectItem>
                              <SelectItem value="480p">SD (480p)</SelectItem>
                              <SelectItem value="360p">Low (360p)</SelectItem>
                              <SelectItem value="audio">🎵 Audio Only</SelectItem>
                            </SelectContent>
                          </Select>

                          <Select value={format} onValueChange={setFormat}>
                            <SelectTrigger className="w-32 bg-slate-900/50">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="mp4">MP4</SelectItem>
                              <SelectItem value="webm">WebM</SelectItem>
                              <SelectItem value="mkv">MKV</SelectItem>
                              <SelectItem value="mp3">MP3</SelectItem>
                              <SelectItem value="m4a">M4A</SelectItem>
                              <SelectItem value="flac">FLAC</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        {/* Speed Limiter */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <Label className="flex items-center gap-2">
                              <Zap className="w-4 h-4" />
                              {t('speedLimiter')} (KB/s)
                            </Label>
                            <span className="text-sm text-muted-foreground">{speedLimit === 0 ? 'Unlimited' : `${speedLimit} KB/s`}</span>
                          </div>
                          <Slider
                            value={[speedLimit]}
                            onValueChange={([value]) => setSpeedLimitValue(value)}
                            max={10240}
                            step={100}
                            className="w-full"
                          />
                        </div>
                      </CardContent>
                    </Card>

                    {/* Drag & Drop Zone */}
                    <DragDropZone onFilesDropped={handleFilesDropped} t={t} />

                    {/* Quick Stats */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      {[
                        { label: t('totalDownloads'), value: stats.total, icon: Download, color: 'cyan' },
                        { label: t('activeDownloads'), value: stats.active, icon: Play, color: 'emerald' },
                        { label: t('completed'), value: stats.completed, icon: CheckCircle2, color: 'cyan' },
                        { label: 'Platforms', value: `${stats.platforms}+`, icon: Globe, color: 'emerald' },
                      ].map((stat, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: i * 0.1 }}
                        >
                          <Card className="bg-slate-800/50 border-slate-700">
                            <CardContent className="p-4">
                              <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg bg-${stat.color}-500/20`}>
                                  <stat.icon className={`w-5 h-5 text-${stat.color}-500`} />
                                </div>
                                <div>
                                  <p className="text-2xl font-bold">{stat.value}</p>
                                  <p className="text-xs text-muted-foreground">{stat.label}</p>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  {/* Right Sidebar */}
                  <div className="space-y-6">
                    <VideoPreview />
                    <Card className="bg-slate-800/50 border-slate-700">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm flex items-center gap-2">
                          <Music className="w-4 h-4" />
                          {t('audioWaveform')}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <AudioWaveform isPlaying={isPlaying} />
                        <div className="flex justify-center gap-2 mt-4">
                          <Button size="sm" variant="outline" onClick={() => setIsPlaying(!isPlaying)}>
                            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </motion.div>
              </AnimatePresence>
            </TabsContent>

            {/* Batch Tab */}
            <TabsContent value="batch" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <Card className="bg-slate-800/50 border-cyan-500/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Layers className="w-5 h-5 text-cyan-500" />
                      {t('batch')} Download
                    </CardTitle>
                    <CardDescription>Download multiple files at once. Paste one URL per line.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Textarea
                      placeholder="Paste URLs here (one per line)&#10;https://youtube.com/watch?v=...&#10;https://tiktok.com/@user/video/...&#10;https://instagram.com/p/..."
                      value={batchUrls}
                      onChange={e => setBatchUrls(e.target.value)}
                      className="min-h-48 bg-slate-900/50 border-cyan-500/30"
                    />
                    <div className="flex flex-wrap gap-4">
                      <Select value={quality} onValueChange={setQuality}>
                        <SelectTrigger className="w-40 bg-slate-900/50">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="best">🏆 Best Quality</SelectItem>
                          <SelectItem value="1080p">Full HD</SelectItem>
                          <SelectItem value="720p">HD</SelectItem>
                          <SelectItem value="audio">🎵 Audio Only</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button
                        onClick={handleBatchDownload}
                        className="bg-gradient-to-r from-cyan-500 to-emerald-500"
                      >
                        <Layers className="w-4 h-4 mr-2" />
                        Start Batch Download
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </TabsContent>

            {/* Downloads Tab */}
            <TabsContent value="downloads" className="space-y-6">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold">{t('downloads')}</h2>
                  <Button variant="outline" onClick={clearCompleted}>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Clear Completed
                  </Button>
                </div>

                {downloads.length === 0 ? (
                  <Card className="bg-slate-800/50">
                    <CardContent className="py-12 text-center">
                      <HardDrive className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground">{t('noDownloads')}</p>
                    </CardContent>
                  </Card>
                ) : (
                  <ScrollArea className="h-[60vh]">
                    <div className="space-y-2">
                      <AnimatePresence>
                        {downloads.map((download) => (
                          <motion.div
                            key={download.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                          >
                            <Card className="bg-slate-800/50 border-slate-700">
                              <CardContent className="p-4">
                                <div className="flex items-start gap-4">
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                      <h3 className="font-medium truncate">{download.title}</h3>
                                      <Badge variant="outline" className={`shrink-0 ${
                                        download.status === 'downloading' ? 'border-cyan-500 text-cyan-500' :
                                        download.status === 'completed' ? 'border-emerald-500 text-emerald-500' :
                                        download.status === 'paused' ? 'border-yellow-500 text-yellow-500' :
                                        download.status === 'scheduled' ? 'border-purple-500 text-purple-500' :
                                        'border-red-500 text-red-500'
                                      }`}>
                                        {download.status === 'downloading' && <Loader2 className="w-3 h-3 mr-1 animate-spin" />}
                                        {download.status.toUpperCase()}
                                      </Badge>
                                    </div>
                                    <p className="text-sm text-muted-foreground truncate mb-2">{download.url}</p>
                                    <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                                      <span>{formatBytes(download.size)}</span>
                                      <span>•</span>
                                      <span>{download.quality}</span>
                                      <span>•</span>
                                      <span>{download.format.toUpperCase()}</span>
                                      {download.status === 'downloading' && (
                                        <>
                                          <span>•</span>
                                          <span className="text-cyan-500">{formatBytes(download.speed)}/s</span>
                                        </>
                                      )}
                                    </div>
                                    {download.status !== 'completed' && download.status !== 'failed' && (
                                      <Progress value={download.progress} className="mt-3 h-2" />
                                    )}
                                  </div>
                                  <div className="flex gap-1">
                                    {download.status === 'downloading' && (
                                      <Button size="icon" variant="ghost">
                                        <Pause className="w-4 h-4" />
                                      </Button>
                                    )}
                                    {download.status === 'paused' && (
                                      <Button size="icon" variant="ghost">
                                        <Play className="w-4 h-4" />
                                      </Button>
                                    )}
                                    <Button size="icon" variant="ghost" className="text-destructive">
                                      <X className="w-4 h-4" />
                                    </Button>
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          </motion.div>
                        ))}
                      </AnimatePresence>
                    </div>
                  </ScrollArea>
                )}
              </motion.div>
            </TabsContent>

            {/* History Tab */}
            <TabsContent value="history" className="space-y-6">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
                  <h2 className="text-2xl font-bold">{t('history')}</h2>
                  <div className="flex flex-wrap gap-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        placeholder={t('searchHistory')}
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        className="pl-10 w-48 bg-slate-900/50"
                      />
                    </div>
                    <Select value={historyFilter} onValueChange={v => setHistoryFilter(v as typeof historyFilter)}>
                      <SelectTrigger className="w-32 bg-slate-900/50">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All</SelectItem>
                        <SelectItem value="video">Video</SelectItem>
                        <SelectItem value="audio">Audio</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button variant="outline" onClick={() => setHistory([])}>
                      <Trash2 className="w-4 h-4 mr-2" />
                      {t('clearHistory')}
                    </Button>
                  </div>
                </div>

                {filteredHistory.length === 0 ? (
                  <Card className="bg-slate-800/50">
                    <CardContent className="py-12 text-center">
                      <History className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground">{t('noHistory')}</p>
                    </CardContent>
                  </Card>
                ) : (
                  <ScrollArea className="h-[60vh]">
                    <div className="space-y-2">
                      {filteredHistory.map((item) => (
                        <Card key={item.id} className="bg-slate-800/50 border-slate-700">
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex-1 min-w-0">
                                <h3 className="font-medium truncate">{item.title}</h3>
                                <p className="text-sm text-muted-foreground truncate">{item.url}</p>
                                <div className="flex flex-wrap gap-2 text-xs text-muted-foreground mt-1">
                                  <span>{formatBytes(item.size)}</span>
                                  <span>•</span>
                                  <span>{item.format.toUpperCase()}</span>
                                  <span>•</span>
                                  <span>{item.quality}</span>
                                  <span>•</span>
                                  <span>{item.downloadedAt.toLocaleDateString()}</span>
                                </div>
                              </div>
                              <div className="flex gap-1">
                                <Button size="icon" variant="ghost" onClick={() => startDownload(item.url)}>
                                  <RefreshCw className="w-4 h-4" />
                                </Button>
                                <Button size="icon" variant="ghost">
                                  <ExternalLink className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </motion.div>
            </TabsContent>

            {/* Platforms Tab */}
            <TabsContent value="platforms" className="space-y-6">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div className="flex items-center gap-4 mb-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      placeholder="Search platforms..."
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                      className="pl-10 bg-slate-900/50"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                  {filteredPlatforms.map((platform, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: idx * 0.02 }}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Card className="bg-slate-800/50 border-slate-700 cursor-pointer hover:border-cyan-500/50 transition-colors">
                        <CardContent className="p-4 text-center">
                          <div className="text-3xl mb-2">{platform.icon}</div>
                          <div className="font-medium text-sm truncate">{platform.name}</div>
                          <div className="text-xs text-muted-foreground">{platform.category}</div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </TabsContent>

            {/* Tools Tab */}
            <TabsContent value="tools" className="space-y-6">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {[
                    { icon: Video, name: 'Video Converter', desc: 'Convert between video formats', color: 'cyan' },
                    { icon: Music, name: 'Audio Extractor', desc: 'Extract audio from videos', color: 'emerald' },
                    { icon: FileText, name: 'Subtitle Downloader', desc: 'Download subtitles', color: 'purple' },
                    { icon: Image, name: 'Thumbnail Grabber', desc: 'Get video thumbnails', color: 'pink' },
                    { icon: Archive, name: 'Metadata Viewer', desc: 'View media metadata', color: 'orange' },
                    { icon: Wrench, name: 'Video Trimmer', desc: 'Trim video clips', color: 'yellow' },
                    { icon: RefreshCw, name: 'Format Converter', desc: 'Batch format conversion', color: 'blue' },
                    { icon: Globe, name: 'Stream Recorder', desc: 'Record live streams', color: 'red' },
                  ].map((tool, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      whileHover={{ scale: 1.02 }}
                    >
                      <Card className="bg-slate-800/50 border-slate-700 cursor-pointer hover:border-cyan-500/50 transition-all">
                        <CardContent className="p-6">
                          <div className={`w-12 h-12 rounded-lg bg-${tool.color}-500/20 flex items-center justify-center mb-4`}>
                            <tool.icon className={`w-6 h-6 text-${tool.color}-500`} />
                          </div>
                          <h3 className="font-semibold mb-1">{tool.name}</h3>
                          <p className="text-sm text-muted-foreground">{tool.desc}</p>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </TabsContent>

            {/* Settings Tab */}
            <TabsContent value="settings" className="space-y-6">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="grid lg:grid-cols-2 gap-6"
              >
                {/* General Settings */}
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="w-5 h-5" />
                      General Settings
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label>{t('theme')}</Label>
                      <Select value={theme} onValueChange={setTheme}>
                        <SelectTrigger className="w-32 bg-slate-900/50">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="light">{t('light')}</SelectItem>
                          <SelectItem value="dark">{t('dark')}</SelectItem>
                          <SelectItem value="system">{t('system')}</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-center justify-between">
                      <Label>{t('language')}</Label>
                      <Select value={language} onValueChange={setLanguage}>
                        <SelectTrigger className="w-32 bg-slate-900/50">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="en">English</SelectItem>
                          <SelectItem value="hi">हिंदी</SelectItem>
                          <SelectItem value="es">Español</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-center justify-between">
                      <Label>{t('soundEnabled')}</Label>
                      <Switch checked={soundEnabled} onCheckedChange={setSoundEnabled} />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label>{t('notifications')}</Label>
                      <Switch checked={notificationsEnabled} onCheckedChange={setNotificationsEnabled} />
                    </div>
                    <Separator />
                    <Button variant="outline" className="w-full" onClick={() => setShowCookieManager(true)}>
                      <Cookie className="w-4 h-4 mr-2" />
                      {t('cookieManager')}
                    </Button>
                    <Button variant="outline" className="w-full" onClick={() => setShowProxyConfig(true)}>
                      <Server className="w-4 h-4 mr-2" />
                      {t('proxyConfig')}
                    </Button>
                  </CardContent>
                </Card>

                {/* Download Settings */}
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Download className="w-5 h-5" />
                      Download Settings
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>Default Quality</Label>
                      <Select value={quality} onValueChange={setQuality}>
                        <SelectTrigger className="bg-slate-900/50">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="best">Best Available</SelectItem>
                          <SelectItem value="2160p">4K Ultra HD</SelectItem>
                          <SelectItem value="1080p">Full HD 1080p</SelectItem>
                          <SelectItem value="720p">HD 720p</SelectItem>
                          <SelectItem value="480p">SD 480p</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Default Format</Label>
                      <Select value={format} onValueChange={setFormat}>
                        <SelectTrigger className="bg-slate-900/50">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="mp4">MP4</SelectItem>
                          <SelectItem value="webm">WebM</SelectItem>
                          <SelectItem value="mkv">MKV</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Max Concurrent Downloads</Label>
                      <Slider defaultValue={[3]} max={10} min={1} step={1} />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label>Auto-start Downloads</Label>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label>Save History</Label>
                      <Switch defaultChecked />
                    </div>
                  </CardContent>
                </Card>

                {/* Data Management */}
                <Card className="bg-slate-800/50 border-slate-700 lg:col-span-2">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <HardDrive className="w-5 h-5" />
                      Data Management
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-4">
                      <Button variant="outline" onClick={exportSettings}>
                        <Export className="w-4 h-4 mr-2" />
                        {t('exportSettings')}
                      </Button>
                      <Button variant="outline" onClick={() => document.getElementById('import-settings')?.click()}>
                        <Import className="w-4 h-4 mr-2" />
                        {t('importSettings')}
                      </Button>
                      <input id="import-settings" type="file" accept=".json" onChange={importSettings} className="hidden" />
                      <Button variant="destructive" onClick={() => { setHistory([]); setDownloads([]); }}>
                        <Trash2 className="w-4 h-4 mr-2" />
                        Clear All Data
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </TabsContent>

            {/* About Tab */}
            <TabsContent value="about" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="max-w-2xl mx-auto"
              >
                <Card className="bg-slate-800/50 border-cyan-500/20">
                  <CardContent className="p-8 text-center">
                    <motion.div
                      initial={{ scale: 0.5 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', duration: 0.5 }}
                      className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent mb-2"
                    >
                      {t('appName')} v3.2.0
                    </motion.div>
                    <p className="text-cyan-500 text-lg mb-6">{t('tagline')} - OMNIPOTENT SOVEREIGN EDITION</p>
                    
                    <p className="text-muted-foreground mb-8">
                      Elite Security Toolkit & Media Downloader<br />
                      50+ Platform Support | Multi-format Download | Batch Processing
                    </p>

                    <div className="bg-cyan-500/10 rounded-xl p-6 mb-8">
                      <p className="font-semibold mb-2">👨‍💻 {t('author')}</p>
                      <p className="text-cyan-500 text-xl">RAJSARASWATI JATAV (RS)</p>
                      <p className="text-muted-foreground">T3rmuxk1ng</p>
                    </div>

                    <div className="grid sm:grid-cols-2 gap-6">
                      <Card className="bg-slate-700/50">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-lg">✨ Features</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <ul className="text-sm text-muted-foreground space-y-1 text-left">
                            <li>• 50+ Platform Support</li>
                            <li>• Real-time WebSocket Progress</li>
                            <li>• Batch Downloads</li>
                            <li>• Video Preview Player</li>
                            <li>• Audio Waveform</li>
                            <li>• Drag & Drop Upload</li>
                            <li>• Keyboard Shortcuts</li>
                            <li>• Multi-language Support</li>
                          </ul>
                        </CardContent>
                      </Card>
                      <Card className="bg-slate-700/50">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-lg">🔒 Security</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <ul className="text-sm text-muted-foreground space-y-1 text-left">
                            <li>• No Data Collection</li>
                            <li>• Local Processing</li>
                            <li>• Encrypted Storage</li>
                            <li>• Privacy First</li>
                            <li>• Open Source</li>
                            <li>• Proxy Support</li>
                            <li>• Cookie Management</li>
                            <li>• Secure Downloads</li>
                          </ul>
                        </CardContent>
                      </Card>
                    </div>

                    <p className="text-muted-foreground text-sm mt-8">
                      Built with React + Next.js + Tailwind CSS + shadcn/ui<br />
                      © 2024 - All Rights Reserved
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            </TabsContent>
          </Tabs>
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-800 py-6 text-center text-sm text-muted-foreground">
          <p>RS TOOLKIT v3.2.0 ULTIMATE NEXUS | © 2024 RAJSARASWATI JATAV (RS) - T3rmuxk1ng</p>
        </footer>

        {/* Modals */}
        <KeyboardShortcutsModal open={showShortcuts} onOpenChange={setShowShortcuts} />
        <CookieManagerDialog
          open={showCookieManager}
          onOpenChange={setShowCookieManager}
          cookies={cookies}
          onAddCookie={addCookie}
          onDeleteCookie={deleteCookie}
        />
        <ProxyConfigDialog
          open={showProxyConfig}
          onOpenChange={setShowProxyConfig}
          proxy={proxyConfig}
          onSave={setProxyConfig}
        />
        <ScheduleDownloadDialog
          open={showScheduleDialog}
          onOpenChange={setShowScheduleDialog}
          onSchedule={scheduleDownload}
        />

        {/* Offline Alert */}
        <AnimatePresence>
          {isOffline && (
            <motion.div
              initial={{ y: 100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 100, opacity: 0 }}
              className="fixed bottom-4 left-4 right-4 z-50"
            >
              <Alert className="bg-destructive/90 text-destructive-foreground border-destructive">
                <WifiOff className="w-4 h-4" />
                <AlertDescription>
                  You are offline. Some features may be limited.
                </AlertDescription>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Toast Notifications */}
        <Toaster />
      </div>
    </TooltipProvider>
  );
}
