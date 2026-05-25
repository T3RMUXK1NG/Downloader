/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * RS TOOLKIT v3.1.0 ULTIMATE NEXUS - Next.js Configuration
 * ═══════════════════════════════════════════════════════════════════════════════
 * Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
 * License: OMNIPOTENT SOVEREIGN NEXUS
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import type { NextConfig } from 'next';

const isDev = process.env.NODE_ENV === 'development';
const isProd = process.env.NODE_ENV === 'production';

const nextConfig: NextConfig = {
  // CRITICAL: Static export for APK/PWA
  output: 'export',
  trailingSlash: true,

  // React settings
  reactStrictMode: true,

  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_APP_NAME: 'RS Toolkit',
    NEXT_PUBLIC_APP_VERSION: '3.1.0',
    NEXT_PUBLIC_APP_EDITION: 'ULTIMATE NEXUS',
    NEXT_PUBLIC_APP_AUTHOR: 'RAJSARASWATI JATAV (RS)',
  },

  // Disable experimental features that don't work with static export
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },

  // Compiler options
  compiler: {
    removeConsole: isProd ? { exclude: ['error', 'warn'] } : false,
  },

  // Webpack config
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        dns: false,
        child_process: false,
        tls: false,
      };
    }
    return config;
  },

  // Disable powered-by header
  poweredByHeader: false,
};

export default nextConfig;
