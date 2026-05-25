/**
 * RS TOOLKIT v3.2.0 ULTIMATE NEXUS - Root Layout
 * Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
 */

import type { Metadata, Viewport } from 'next';
import { ThemeProvider } from 'next-themes';
import './globals.css';

export const metadata: Metadata = {
  title: 'RS Toolkit v3.2.0 - Ultimate Nexus',
  description: 'Elite Security Toolkit & Media Downloader by T3rmuxk1ng - 50+ Platform Support',
  keywords: ['downloader', 'youtube', 'tiktok', 'instagram', 'media', 'video', 'audio', 'security', 'toolkit'],
  authors: [{ name: 'RAJSARASWATI JATAV (RS)', url: 'https://github.com/T3RMUXK1NG' }],
  creator: 'RAJSARASWATI JATAV (RS)',
  publisher: 'T3rmuxk1ng',
  applicationName: 'RS Toolkit',
  version: '3.2.0',
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
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f0f19' },
  ],
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
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
