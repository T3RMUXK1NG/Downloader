/**
 * RS TOOLKIT v3.1.0 ULTIMATE NEXUS - Root Layout
 * Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
 */

import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'RS Toolkit v3.1.0 - Ultimate Nexus',
  description: 'Elite Security Toolkit & Media Downloader by T3rmuxk1ng - 50+ Platform Support',
  keywords: ['downloader', 'youtube', 'tiktok', 'instagram', 'media', 'video', 'audio', 'security', 'toolkit'],
  authors: [{ name: 'RAJSARASWATI JATAV (RS)', url: 'https://github.com/T3RMUXK1NG' }],
  creator: 'RAJSARASWATI JATAV (RS)',
  publisher: 'T3rmuxk1ng',
  applicationName: 'RS Toolkit',
  version: '3.1.0',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'RS Toolkit',
  },
  formatDetection: {
    telephone: false,
  },
};

export const viewport: Viewport = {
  themeColor: '#0f0f19',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
      </head>
      <body>{children}</body>
    </html>
  );
}
