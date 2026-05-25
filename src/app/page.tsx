/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * RS TOOLKIT v3.1.0 ULTIMATE NEXUS - Main Application
 * ═══════════════════════════════════════════════════════════════════════════════
 * Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
 * License: OMNIPOTENT SOVEREIGN NEXUS
 * ═══════════════════════════════════════════════════════════════════════════════
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';

// ============================================================================
// TYPES
// ============================================================================

interface DownloadItem {
  id: string;
  url: string;
  title: string;
  status: 'pending' | 'downloading' | 'completed' | 'failed' | 'paused';
  progress: number;
  speed: number;
  size: number;
  format: string;
  quality: string;
  createdAt: Date;
}

interface HistoryItem {
  id: string;
  url: string;
  title: string;
  format: string;
  quality: string;
  size: number;
  downloadedAt: Date;
}

interface Platform {
  name: string;
  icon: string;
  category: string;
  url: string;
}

// ============================================================================
// PLATFORMS DATA
// ============================================================================

const PLATFORMS: Platform[] = [
  // Video Platforms
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
  // Music Platforms
  { name: 'Spotify', icon: '🎧', category: 'Music', url: 'spotify.com' },
  { name: 'SoundCloud', icon: '☁️', category: 'Music', url: 'soundcloud.com' },
  { name: 'Apple Music', icon: '🍎', category: 'Music', url: 'music.apple.com' },
  { name: 'Deezer', icon: '🎼', category: 'Music', url: 'deezer.com' },
  { name: 'Bandcamp', icon: '📀', category: 'Music', url: 'bandcamp.com' },
  { name: 'Audiomack', icon: '🔊', category: 'Music', url: 'audiomack.com' },
  // Other Platforms
  { name: 'MediaFire', icon: '🔥', category: 'Cloud', url: 'mediafire.com' },
  { name: 'Google Drive', icon: '📁', category: 'Cloud', url: 'drive.google.com' },
  { name: 'Dropbox', icon: '📦', category: 'Cloud', url: 'dropbox.com' },
  { name: 'Mega', icon: '🔐', category: 'Cloud', url: 'mega.nz' },
  { name: 'Imgur', icon: '🖼️', category: 'Image', url: 'imgur.com' },
  { name: 'Gfycat', icon: '🐱', category: 'GIF', url: 'gfycat.com' },
  { name: 'Streamable', icon: '🎞️', category: 'Video', url: 'streamable.com' },
  { name: 'OK.ru', icon: '👌', category: 'Video', url: 'ok.ru' },
  { name: 'VK', icon: '💬', category: 'Social', url: 'vk.com' },
  { name: 'Pornhub', icon: '🔞', category: 'Adult', url: 'pornhub.com' },
  { name: 'XVideos', icon: '🔞', category: 'Adult', url: 'xvideos.com' },
  { name: 'YouPorn', icon: '🔞', category: 'Adult', url: 'youporn.com' },
  { name: 'XNXX', icon: '🔞', category: 'Adult', url: 'xnxx.com' },
  { name: 'SpankBang', icon: '🔞', category: 'Adult', url: 'spankbang.com' },
  { name: 'RedTube', icon: '🔞', category: 'Adult', url: 'redtube.com' },
  { name: ' xnxx', icon: '🔞', category: 'Adult', url: 'xnxx.com' },
  { name: 'Eporner', icon: '🔞', category: 'Adult', url: 'eporner.com' },
  { name: 'YouJizz', icon: '🔞', category: 'Adult', url: 'youjizz.com' },
  { name: 'Tube8', icon: '🔞', category: 'Adult', url: 'tube8.com' },
  { name: 'XTube', icon: '🔞', category: 'Adult', url: 'xtube.com' },
  { name: 'Thumbzilla', icon: '🔞', category: 'Adult', url: 'thumbzilla.com' },
  { name: 'Pornone', icon: '🔞', category: 'Adult', url: 'pornone.com' },
  { name: 'HClips', icon: '🔞', category: 'Adult', url: 'hclips.com' },
  { name: 'PornHat', icon: '🔞', category: 'Adult', url: 'pornhat.com' },
  { name: 'PornGo', icon: '🔞', category: 'Adult', url: 'porngo.com' },
  { name: 'PornTrex', icon: '🔞', category: 'Adult', url: 'porntrex.com' },
  { name: 'PornHD', icon: '🔞', category: 'Adult', url: 'pornhd.com' },
  { name: 'PornTube', icon: '🔞', category: 'Adult', url: 'porntube.com' },
  { name: 'SunPorno', icon: '🔞', category: 'Adult', url: 'sunporno.com' },
  { name: 'PornoMovies', icon: '🔞', category: 'Adult', url: 'pornomovies.com' },
  { name: 'TubePornClassic', icon: '🔞', category: 'Adult', url: 'tubepornclassic.com' },
];

// ============================================================================
// STYLES
// ============================================================================

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f0f19 0%, #1a1a2e 50%, #16213e 100%)',
    color: '#ffffff',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  header: {
    padding: '16px 24px',
    background: 'rgba(15, 15, 25, 0.9)',
    backdropFilter: 'blur(10px)',
    borderBottom: '1px solid rgba(0, 200, 255, 0.2)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  logo: {
    fontSize: '24px',
    fontWeight: 'bold',
    background: 'linear-gradient(90deg, #00c8ff, #00ff88)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  tabs: {
    display: 'flex',
    gap: '4px',
    padding: '12px 24px',
    overflowX: 'auto' as const,
    background: 'rgba(15, 15, 25, 0.5)',
    borderBottom: '1px solid rgba(0, 200, 255, 0.1)',
  },
  tab: {
    padding: '10px 20px',
    borderRadius: '8px',
    border: 'none',
    background: 'transparent',
    color: '#888',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    transition: 'all 0.3s ease',
    whiteSpace: 'nowrap' as const,
  },
  tabActive: {
    background: 'linear-gradient(135deg, #00c8ff 0%, #00ff88 100%)',
    color: '#0f0f19',
  },
  content: {
    padding: '24px',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  card: {
    background: 'rgba(26, 26, 46, 0.8)',
    borderRadius: '16px',
    padding: '24px',
    marginBottom: '16px',
    border: '1px solid rgba(0, 200, 255, 0.1)',
  },
  input: {
    width: '100%',
    padding: '16px',
    borderRadius: '12px',
    border: '2px solid rgba(0, 200, 255, 0.3)',
    background: 'rgba(15, 15, 25, 0.8)',
    color: '#fff',
    fontSize: '16px',
    outline: 'none',
    transition: 'border-color 0.3s',
    marginBottom: '16px',
  },
  button: {
    padding: '14px 28px',
    borderRadius: '12px',
    border: 'none',
    background: 'linear-gradient(135deg, #00c8ff 0%, #00ff88 100%)',
    color: '#0f0f19',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'transform 0.3s, box-shadow 0.3s',
  },
  buttonSecondary: {
    padding: '12px 24px',
    borderRadius: '10px',
    border: '2px solid rgba(0, 200, 255, 0.5)',
    background: 'transparent',
    color: '#00c8ff',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  select: {
    padding: '12px 16px',
    borderRadius: '10px',
    border: '2px solid rgba(0, 200, 255, 0.3)',
    background: 'rgba(15, 15, 25, 0.8)',
    color: '#fff',
    fontSize: '14px',
    outline: 'none',
    cursor: 'pointer',
  },
  downloadItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '16px',
    background: 'rgba(15, 15, 25, 0.6)',
    borderRadius: '12px',
    marginBottom: '12px',
    border: '1px solid rgba(0, 200, 255, 0.1)',
  },
  progressBar: {
    height: '6px',
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '3px',
    overflow: 'hidden',
    flex: 1,
  },
  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #00c8ff, #00ff88)',
    borderRadius: '3px',
    transition: 'width 0.3s ease',
  },
  platformGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
    gap: '12px',
  },
  platformCard: {
    padding: '16px',
    background: 'rgba(15, 15, 25, 0.6)',
    borderRadius: '12px',
    textAlign: 'center' as const,
    border: '1px solid rgba(0, 200, 255, 0.1)',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  badge: {
    padding: '4px 10px',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: '600',
  },
  flexRow: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap' as const,
  },
  textMuted: {
    color: '#888',
    fontSize: '14px',
  },
  textSmall: {
    color: '#666',
    fontSize: '12px',
  },
  h2: {
    fontSize: '22px',
    fontWeight: 'bold',
    marginBottom: '16px',
    color: '#fff',
  },
  h3: {
    fontSize: '18px',
    fontWeight: '600',
    marginBottom: '12px',
    color: '#fff',
  },
  grid2: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
  },
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function RSToolkitApp() {
  // State
  const [activeTab, setActiveTab] = useState('download');
  const [url, setUrl] = useState('');
  const [quality, setQuality] = useState('best');
  const [format, setFormat] = useState('mp4');
  const [downloads, setDownloads] = useState<DownloadItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [batchUrls, setBatchUrls] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

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

  // Simulate download
  const startDownload = useCallback((downloadUrl: string) => {
    const newDownload: DownloadItem = {
      id: generateId(),
      url: downloadUrl,
      title: `Media from ${new URL(downloadUrl).hostname}`,
      status: 'downloading',
      progress: 0,
      speed: Math.floor(Math.random() * 5000000) + 1000000,
      size: Math.floor(Math.random() * 500000000) + 10000000,
      format,
      quality,
      createdAt: new Date(),
    };

    setDownloads(prev => [newDownload, ...prev]);

    // Simulate progress
    const interval = setInterval(() => {
      setDownloads(prev => {
        const updated = prev.map(d => {
          if (d.id === newDownload.id && d.status === 'downloading') {
            const newProgress = Math.min(d.progress + Math.random() * 15, 100);
            if (newProgress >= 100) {
              clearInterval(interval);
              // Add to history
              setHistory(h => [{
                id: d.id,
                url: d.url,
                title: d.title,
                format: d.format,
                quality: d.quality,
                size: d.size,
                downloadedAt: new Date(),
              }, ...h]);
              return { ...d, progress: 100, status: 'completed' };
            }
            return { ...d, progress: newProgress };
          }
          return d;
        });
        return updated;
      });
    }, 500);

    return () => clearInterval(interval);
  }, [format, quality]);

  // Handle single download
  const handleDownload = () => {
    if (!url.trim()) return;
    try {
      new URL(url);
      startDownload(url);
      setUrl('');
    } catch {
      alert('Please enter a valid URL');
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

  // Clear completed
  const clearCompleted = () => {
    setDownloads(prev => prev.filter(d => d.status !== 'completed'));
  };

  // Filter platforms
  const filteredPlatforms = PLATFORMS.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Stats
  const stats = {
    total: downloads.length + history.length,
    completed: history.length,
    active: downloads.filter(d => d.status === 'downloading').length,
    platforms: PLATFORMS.length,
  };

  // Render tabs
  const tabs = [
    { id: 'download', label: '📥 Download', icon: '📥' },
    { id: 'batch', label: '📦 Batch', icon: '📦' },
    { id: 'downloads', label: '⬇️ Downloads', icon: '⬇️' },
    { id: 'history', label: '📜 History', icon: '📜' },
    { id: 'platforms', label: '🌐 Platforms', icon: '🌐' },
    { id: 'tools', label: '🔧 Tools', icon: '🔧' },
    { id: 'settings', label: '⚙️ Settings', icon: '⚙️' },
    { id: 'about', label: 'ℹ️ About', icon: 'ℹ️' },
  ];

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.logo}>RS TOOLKIT v3.1.0</div>
        <div style={styles.textMuted}>ULTIMATE NEXUS</div>
      </header>

      {/* Tabs */}
      <nav style={styles.tabs}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            style={{
              ...styles.tab,
              ...(activeTab === tab.id ? styles.tabActive : {}),
            }}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Content */}
      <main style={styles.content}>
        {/* Download Tab */}
        {activeTab === 'download' && (
          <div>
            <div style={styles.card}>
              <h2 style={styles.h2}>📥 Download Media</h2>
              <p style={styles.textMuted}>
                Paste any URL from 50+ supported platforms. Automatic format detection and quality selection.
              </p>
              <input
                style={styles.input}
                type="url"
                placeholder="Paste URL here (YouTube, TikTok, Instagram, etc.)"
                value={url}
                onChange={e => setUrl(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleDownload()}
              />
              <div style={styles.flexRow}>
                <select
                  style={styles.select}
                  value={quality}
                  onChange={e => setQuality(e.target.value)}
                >
                  <option value="best">🏆 Best Quality</option>
                  <option value="2160p">4K (2160p)</option>
                  <option value="1080p">Full HD (1080p)</option>
                  <option value="720p">HD (720p)</option>
                  <option value="480p">SD (480p)</option>
                  <option value="360p">Low (360p)</option>
                  <option value="audio">🎵 Audio Only</option>
                </select>
                <select
                  style={styles.select}
                  value={format}
                  onChange={e => setFormat(e.target.value)}
                >
                  <option value="mp4">MP4 Video</option>
                  <option value="webm">WebM Video</option>
                  <option value="mkv">MKV Video</option>
                  <option value="mp3">MP3 Audio</option>
                  <option value="m4a">M4A Audio</option>
                  <option value="flac">FLAC Audio</option>
                </select>
                <button style={styles.button} onClick={handleDownload}>
                  ⬇️ Download
                </button>
              </div>
            </div>

            {/* Quick Stats */}
            <div style={styles.grid2}>
              <div style={styles.card}>
                <div style={styles.textMuted}>Total Downloads</div>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#00c8ff' }}>
                  {stats.total}
                </div>
              </div>
              <div style={styles.card}>
                <div style={styles.textMuted}>Active Downloads</div>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#00ff88' }}>
                  {stats.active}
                </div>
              </div>
              <div style={styles.card}>
                <div style={styles.textMuted}>Completed</div>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#00c8ff' }}>
                  {stats.completed}
                </div>
              </div>
              <div style={styles.card}>
                <div style={styles.textMuted}>Platforms</div>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#00ff88' }}>
                  {stats.platforms}+
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Batch Tab */}
        {activeTab === 'batch' && (
          <div>
            <div style={styles.card}>
              <h2 style={styles.h2}>📦 Batch Download</h2>
              <p style={styles.textMuted}>
                Download multiple files at once. Paste one URL per line.
              </p>
              <textarea
                style={{
                  ...styles.input,
                  minHeight: '200px',
                  resize: 'vertical' as const,
                }}
                placeholder="Paste URLs here (one per line)&#10;https://youtube.com/watch?v=...&#10;https://tiktok.com/@user/video/...&#10;https://instagram.com/p/..."
                value={batchUrls}
                onChange={e => setBatchUrls(e.target.value)}
              />
              <div style={styles.flexRow}>
                <select style={styles.select} value={quality} onChange={e => setQuality(e.target.value)}>
                  <option value="best">🏆 Best Quality</option>
                  <option value="1080p">Full HD</option>
                  <option value="720p">HD</option>
                  <option value="audio">🎵 Audio Only</option>
                </select>
                <button style={styles.button} onClick={handleBatchDownload}>
                  📦 Start Batch Download
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Downloads Tab */}
        {activeTab === 'downloads' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={styles.h2}>⬇️ Active Downloads</h2>
              <button style={styles.buttonSecondary} onClick={clearCompleted}>
                Clear Completed
              </button>
            </div>
            {downloads.length === 0 ? (
              <div style={styles.card}>
                <p style={styles.textMuted}>No active downloads. Start downloading from the Download tab!</p>
              </div>
            ) : (
              downloads.map(download => (
                <div key={download.id} style={styles.downloadItem}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: '600', marginBottom: '8px' }}>{download.title}</div>
                    <div style={styles.textSmall}>{download.url}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '8px' }}>
                      <span style={{
                        ...styles.badge,
                        background: download.status === 'downloading' ? 'rgba(0, 200, 255, 0.2)' :
                          download.status === 'completed' ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255, 100, 100, 0.2)',
                        color: download.status === 'downloading' ? '#00c8ff' :
                          download.status === 'completed' ? '#00ff88' : '#ff6464',
                      }}>
                        {download.status.toUpperCase()}
                      </span>
                      <span style={styles.textSmall}>{formatBytes(download.size)}</span>
                      <span style={styles.textSmall}>{download.quality}</span>
                      <span style={styles.textSmall}>{download.format.toUpperCase()}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '12px' }}>
                      <div style={styles.progressBar}>
                        <div style={{ ...styles.progressFill, width: `${download.progress}%` }} />
                      </div>
                      <span style={styles.textSmall}>{download.progress.toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div>
            <h2 style={styles.h2}>📜 Download History</h2>
            {history.length === 0 ? (
              <div style={styles.card}>
                <p style={styles.textMuted}>No download history yet. Your completed downloads will appear here.</p>
              </div>
            ) : (
              history.map(item => (
                <div key={item.id} style={styles.downloadItem}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: '600' }}>{item.title}</div>
                    <div style={styles.textSmall}>{item.url}</div>
                    <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
                      <span style={styles.textSmall}>{formatBytes(item.size)}</span>
                      <span style={styles.textSmall}>{item.format.toUpperCase()}</span>
                      <span style={styles.textSmall}>{item.quality}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Platforms Tab */}
        {activeTab === 'platforms' && (
          <div>
            <h2 style={styles.h2}>🌐 Supported Platforms</h2>
            <input
              style={styles.input}
              type="text"
              placeholder="🔍 Search platforms..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
            <div style={styles.platformGrid}>
              {filteredPlatforms.map((platform, idx) => (
                <div
                  key={idx}
                  style={styles.platformCard}
                  onMouseEnter={e => {
                    e.currentTarget.style.transform = 'scale(1.05)';
                    e.currentTarget.style.borderColor = 'rgba(0, 200, 255, 0.5)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = 'scale(1)';
                    e.currentTarget.style.borderColor = 'rgba(0, 200, 255, 0.1)';
                  }}
                >
                  <div style={{ fontSize: '32px', marginBottom: '8px' }}>{platform.icon}</div>
                  <div style={{ fontWeight: '600', fontSize: '14px' }}>{platform.name}</div>
                  <div style={styles.textSmall}>{platform.category}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tools Tab */}
        {activeTab === 'tools' && (
          <div>
            <h2 style={styles.h2}>🔧 Tools & Features</h2>
            <div style={styles.grid2}>
              {[
                { icon: '🎬', name: 'Video Converter', desc: 'Convert between video formats' },
                { icon: '🎵', name: 'Audio Extractor', desc: 'Extract audio from videos' },
                { icon: '📝', name: 'Subtitle Downloader', desc: 'Download subtitles' },
                { icon: '🖼️', name: 'Thumbnail Grabber', desc: 'Get video thumbnails' },
                { icon: '📊', name: 'Metadata Viewer', desc: 'View media metadata' },
                { icon: '✂️', name: 'Video Trimmer', desc: 'Trim video clips' },
                { icon: '🔄', name: 'Format Converter', desc: 'Batch format conversion' },
                { icon: '📡', name: 'Stream Recorder', desc: 'Record live streams' },
              ].map((tool, idx) => (
                <div key={idx} style={styles.card}>
                  <div style={{ fontSize: '32px', marginBottom: '12px' }}>{tool.icon}</div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>{tool.name}</div>
                  <div style={styles.textMuted}>{tool.desc}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div>
            <h2 style={styles.h2}>⚙️ Settings</h2>
            <div style={styles.card}>
              <h3 style={styles.h3}>Download Settings</h3>
              <div style={styles.flexRow}>
                <select style={styles.select}>
                  <option>📱 Internal Storage</option>
                  <option>💾 SD Card</option>
                  <option>☁️ Cloud Storage</option>
                </select>
              </div>
            </div>
            <div style={styles.card}>
              <h3 style={styles.h3}>Quality Preferences</h3>
              <div style={styles.flexRow}>
                <select style={styles.select} defaultValue="1080p">
                  <option value="best">🏆 Best Available</option>
                  <option value="2160p">4K Ultra HD</option>
                  <option value="1080p">Full HD 1080p</option>
                  <option value="720p">HD 720p</option>
                  <option value="480p">SD 480p</option>
                </select>
                <select style={styles.select} defaultValue="mp4">
                  <option value="mp4">MP4</option>
                  <option value="webm">WebM</option>
                  <option value="mkv">MKV</option>
                </select>
              </div>
            </div>
            <div style={styles.card}>
              <h3 style={styles.h3}>Audio Settings</h3>
              <div style={styles.flexRow}>
                <select style={styles.select} defaultValue="320">
                  <option value="320">320 kbps (High)</option>
                  <option value="256">256 kbps</option>
                  <option value="192">192 kbps</option>
                  <option value="128">128 kbps</option>
                </select>
                <select style={styles.select} defaultValue="mp3">
                  <option value="mp3">MP3</option>
                  <option value="m4a">M4A/AAC</option>
                  <option value="flac">FLAC (Lossless)</option>
                  <option value="ogg">OGG Vorbis</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* About Tab */}
        {activeTab === 'about' && (
          <div>
            <div style={styles.card}>
              <h2 style={{ ...styles.h2, textAlign: 'center' as const }}>
                RS TOOLKIT v3.1.0
              </h2>
              <p style={{ textAlign: 'center' as const, color: '#00c8ff', fontSize: '18px', marginBottom: '16px' }}>
                ULTIMATE NEXUS - OMNIPOTENT SOVEREIGN EDITION
              </p>
              <div style={{ textAlign: 'center' as const, marginBottom: '24px' }}>
                <p style={styles.textMuted}>
                  Elite Security Toolkit & Media Downloader
                </p>
                <p style={styles.textMuted}>
                  50+ Platform Support | Multi-format Download | Batch Processing
                </p>
              </div>
              <div style={{ textAlign: 'center' as const, padding: '20px', background: 'rgba(0, 200, 255, 0.1)', borderRadius: '12px' }}>
                <p style={{ fontWeight: '600', marginBottom: '8px' }}>👨‍💻 Author</p>
                <p style={{ color: '#00c8ff', fontSize: '18px' }}>RAJSARASWATI JATAV (RS)</p>
                <p style={styles.textMuted}>T3rmuxk1ng</p>
              </div>
              <div style={{ marginTop: '24px', textAlign: 'center' as const }}>
                <p style={styles.textSmall}>Built with React + Next.js + Capacitor</p>
                <p style={styles.textSmall}>© 2024 - All Rights Reserved</p>
              </div>
            </div>

            <div style={styles.grid2}>
              <div style={styles.card}>
                <h3 style={styles.h3}>✨ Features</h3>
                <ul style={{ color: '#888', paddingLeft: '20px' }}>
                  <li>50+ Platform Support</li>
                  <li>Batch Downloads</li>
                  <li>Quality Selection</li>
                  <li>Format Conversion</li>
                  <li>Subtitle Download</li>
                  <li>Metadata Extraction</li>
                </ul>
              </div>
              <div style={styles.card}>
                <h3 style={styles.h3}>🔒 Security</h3>
                <ul style={{ color: '#888', paddingLeft: '20px' }}>
                  <li>No Data Collection</li>
                  <li>Local Processing</li>
                  <li>Encrypted Storage</li>
                  <li>Privacy First</li>
                  <li>Open Source</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{ padding: '24px', textAlign: 'center' as const, color: '#666' }}>
        <p>RS TOOLKIT v3.1.0 ULTIMATE NEXUS | © 2024 RAJSARASWATI JATAV (RS) - T3rmuxk1ng</p>
      </footer>
    </div>
  );
}
