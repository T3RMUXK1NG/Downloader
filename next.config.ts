/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * RS TOOLKIT v3.1.1 ULTIMATE NEXUS - Next.js Configuration
 * ═══════════════════════════════════════════════════════════════════════════════
 * Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
 * License: OMNIPOTENT SOVEREIGN NEXUS
 * 
 * Hybrid Mode: Next.js Frontend + Python Backend + APK Support
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import type { NextConfig } from 'next';

const isDev = process.env.NODE_ENV === 'development';
const isProd = process.env.NODE_ENV === 'production';

const nextConfig: NextConfig = {
  // Standalone for API routes support
  output: 'standalone',
  
  // React settings
  reactStrictMode: true,

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    unoptimized: true,
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_APP_NAME: 'RS Toolkit',
    NEXT_PUBLIC_APP_VERSION: '3.1.1',
    NEXT_PUBLIC_APP_EDITION: 'ULTIMATE NEXUS',
    NEXT_PUBLIC_APP_AUTHOR: 'RAJSARASWATI JATAV (RS)',
    NEXT_PUBLIC_PYTHON_BACKEND: 'http://localhost:8000',
  },

  // Experimental features
  experimental: {
    serverActions: {
      bodySizeLimit: '50mb',
    },
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

  // API rewrites to Python backend
  async rewrites() {
    return [
      {
        source: '/api/python/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },

  // Disable powered-by header
  poweredByHeader: false,
};

export default nextConfig;
