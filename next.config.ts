import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",

  // TypeScript configuration
  typescript: {
    ignoreBuildErrors: true,
  },

  // React configuration
  reactStrictMode: false,

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'img.youtube.com',
      },
      {
        protocol: 'https',
        hostname: 'i.ytimg.com',
      },
      {
        protocol: 'https',
        hostname: '*.ytimg.com',
      },
    ],
    unoptimized: true,
  },

  // Experimental features
  experimental: {
    serverActions: {
      bodySizeLimit: '100mb',
    },
  },

  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_APP_NAME: 'RS Downloader Toolkit',
    NEXT_PUBLIC_APP_VERSION: '2.1.0',
    NEXT_PUBLIC_AUTHOR: 'RS (T3rmuxk1ng)',
  },
};

export default nextConfig;
