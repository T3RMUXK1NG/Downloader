/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * RS TOOLKIT v3.0.1 ULTIMATE NEXUS - Next.js Configuration
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
 * License: OMNIPOTENT SOVEREIGN NEXUS
 *
 * This configuration provides comprehensive settings for:
 * - Performance optimization with Turbopack
 * - Security headers and CSP
 * - Image optimization
 * - Bundle analysis
 * - PWA support
 * - Internationalization
 * - Experimental features
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import type { NextConfig } from 'next';
import bundleAnalyzer from '@next/bundle-analyzer';

// ═══════════════════════════════════════════════════════════════════════════════
// ENVIRONMENT VARIABLES
// ═══════════════════════════════════════════════════════════════════════════════

const isDev = process.env.NODE_ENV === 'development';
const isProd = process.env.NODE_ENV === 'production';
const isAnalyze = process.env.ANALYZE === 'true';

// ═══════════════════════════════════════════════════════════════════════════════
// BUNDLE ANALYZER PLUGIN
// ═══════════════════════════════════════════════════════════════════════════════

const withBundleAnalyzer = bundleAnalyzer({
  enabled: isAnalyze,
  openAnalyzer: true,
  analyzerMode: 'static',
  reportFilename: '../analyze/client.html',
});

// ═══════════════════════════════════════════════════════════════════════════════
// SECURITY HEADERS CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const securityHeaders = [
  // Prevent clickjacking
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  // Prevent MIME type sniffing
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  // XSS Protection
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block',
  },
  // Referrer Policy
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  // Permissions Policy (Feature Policy)
  {
    key: 'Permissions-Policy',
    value: [
      'camera=(self)',
      'microphone=(self)',
      'geolocation=(self)',
      'payment=()',
      'usb=()',
      'magnetometer=()',
      'gyroscope=()',
      'accelerometer=()',
    ].join(', '),
  },
  // Content Security Policy
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.jsdelivr.net",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob: https: http:",
      "font-src 'self' data:",
      "connect-src 'self' https: wss:",
      "media-src 'self' blob: data:",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "upgrade-insecure-requests",
    ].join('; '),
  },
  // Strict Transport Security (HSTS)
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN NEXT.JS CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const nextConfig: NextConfig = {
  // ─────────────────────────────────────────────────────────────────────────────
  // REACT OPTIONS
  // ─────────────────────────────────────────────────────────────────────────────

  reactStrictMode: true,
  reactProductionProfiling: isProd,

  // ─────────────────────────────────────────────────────────────────────────────
  // OUTPUT CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  output: 'standalone',
  trailingSlash: false,

  // ─────────────────────────────────────────────────────────────────────────────
  // TURBOPACK CONFIGURATION (Development)
  // ─────────────────────────────────────────────────────────────────────────────

  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
    resolveExtensions: ['.tsx', '.ts', '.jsx', '.js', '.json', '.mjs'],
    moduleIds: 'deterministic',
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // IMAGE OPTIMIZATION
  // ─────────────────────────────────────────────────────────────────────────────

  images: {
    formats: ['image/avif', 'image/webp'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
    unoptimized: isDev,
    dangerouslyAllowSVG: true,
    contentDispositionType: 'attachment',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // HEADERS CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
      {
        // Cache static assets
        source: '/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        // Cache images
        source: '/images/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        // Cache fonts
        source: '/fonts/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // REDIRECTS CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  async redirects() {
    return [
      // Redirect old routes
      {
        source: '/download',
        destination: '/tools/download',
        permanent: true,
      },
      {
        source: '/tools',
        destination: '/',
        permanent: true,
      },
      // Security: Redirect common attack paths
      {
        source: '/.env',
        destination: '/',
        permanent: false,
      },
      {
        source: '/.git/:path*',
        destination: '/',
        permanent: false,
      },
      {
        source: '/wp-admin/:path*',
        destination: '/',
        permanent: false,
      },
      {
        source: '/wp-login.php',
        destination: '/',
        permanent: false,
      },
    ];
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // REWRITES CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  async rewrites() {
    return {
      beforeFiles: [
        // API proxy for backend
        {
          source: '/api/backend/:path*',
          destination: 'http://localhost:8000/api/:path*',
        },
      ],
      afterFiles: [
        // PWA service worker
        {
          source: '/sw.js',
          destination: '/api/sw',
        },
      ],
      fallback: [
        // SPA fallback for dynamic routes
        {
          source: '/app/:path*',
          destination: '/app',
        },
      ],
    };
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // ENVIRONMENT VARIABLES
  // ─────────────────────────────────────────────────────────────────────────────

  env: {
    NEXT_PUBLIC_APP_NAME: 'RS Toolkit',
    NEXT_PUBLIC_APP_VERSION: '3.0.1',
    NEXT_PUBLIC_APP_EDITION: 'ULTIMATE NEXUS',
    NEXT_PUBLIC_APP_AUTHOR: 'RAJSARASWATI JATAV (RS)',
    NEXT_PUBLIC_BUILD_TIME: new Date().toISOString(),
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // WEBPACK CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Enable top-level await
    config.experiments = {
      ...config.experiments,
      topLevelAwait: true,
    };

    // Ignore specific warnings
    config.ignoreWarnings = [
      { module: /node_modules\/undici/ },
      { module: /node_modules\/@prisma\/client/ },
      { file: /node_modules\/ws\/lib\/buffer-util\.js/ },
    ];

    // Add custom plugins
    config.plugins.push(
      new webpack.DefinePlugin({
        __BUILD_ID__: JSON.stringify(buildId),
        __DEV__: JSON.stringify(dev),
        __SERVER__: JSON.stringify(isServer),
      })
    );

    // Resolve fallbacks for browser
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        dns: false,
        child_process: false,
        tls: false,
        crypto: require.resolve('crypto-browserify'),
        stream: require.resolve('stream-browserify'),
        buffer: require.resolve('buffer/'),
        path: require.resolve('path-browserify'),
        os: require.resolve('os-browserify/browser'),
        http: require.resolve('stream-http'),
        https: require.resolve('https-browserify'),
        zlib: require.resolve('browserify-zlib'),
        url: require.resolve('url/'),
      };
    }

    // Module rules
    config.module.rules.push(
      // Handle SVG as React components
      {
        test: /\.svg$/i,
        issuer: /\.[jt]sx?$/,
        use: [
          {
            loader: '@svgr/webpack',
            options: {
              prettier: false,
              svgo: true,
              svgoConfig: {
                plugins: [
                  {
                    name: 'preset-default',
                    params: {
                      overrides: {
                        removeViewBox: false,
                      },
                    },
                  },
                ],
              },
            },
          },
        ],
      }
    );

    // Optimization
    config.optimization = {
      ...config.optimization,
      moduleIds: 'deterministic',
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          // Framework chunk
          framework: {
            name: 'framework',
            test: /[\\/]node_modules[\\/](react|react-dom|scheduler|prop-types)[\\/]/,
            priority: 40,
            enforce: true,
          },
          // Vendor chunk
          vendor: {
            name: 'vendor',
            test: /[\\/]node_modules[\\/]/,
            priority: 30,
            minChunks: 2,
          },
          // Common chunk
          common: {
            name: 'common',
            minChunks: 2,
            priority: 20,
          },
        },
      },
    };

    return config;
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // EXPERIMENTAL FEATURES
  // ─────────────────────────────────────────────────────────────────────────────

  experimental: {
    // Enable PPR (Partial Prerendering)
    ppr: true,

    // Enable Server Actions
    serverActions: {
      bodySizeLimit: '10mb',
      allowedOrigins: ['*.t3rmuxk1ng.com', 'localhost:3000'],
    },

    // Enable optimistic client cache
    optimisticClientCache: true,

    // Enable memory-based routing
    optimistic: true,

    // Stale times
    staleTimes: {
      dynamic: 30,
      static: 300,
    },

    // Enable turbo for dev
    turbo: {
      enabled: true,
    },

    // Enable typed routes
    typedRoutes: true,

    // Enable optimized package imports
    optimizePackageImports: [
      '@radix-ui/react-accordion',
      '@radix-ui/react-alert-dialog',
      '@radix-ui/react-avatar',
      '@radix-ui/react-checkbox',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-label',
      '@radix-ui/react-popover',
      '@radix-ui/react-progress',
      '@radix-ui/react-scroll-area',
      '@radix-ui/react-select',
      '@radix-ui/react-separator',
      '@radix-ui/react-slider',
      '@radix-ui/react-slot',
      '@radix-ui/react-switch',
      '@radix-ui/react-tabs',
      '@radix-ui/react-toast',
      '@radix-ui/react-tooltip',
      'lucide-react',
      'framer-motion',
      'date-fns',
    ],

    // Server components
    serverComponentsExternalPackages: [
      'bcryptjs',
      'jsonwebtoken',
      'sharp',
      'ffmpeg-static',
      'puppeteer',
      'playwright-core',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // CACHING
  // ─────────────────────────────────────────────────────────────────────────────

  generateBuildId: async () => {
    return `rs-toolkit-${Date.now()}`;
  },

  generateEtags: true,

  // ─────────────────────────────────────────────────────────────────────────────
  // COMPILER OPTIONS
  // ─────────────────────────────────────────────────────────────────────────────

  compiler: {
    // Enable SWC minification
    removeConsole: isProd
      ? {
          exclude: ['error', 'warn'],
        }
      : false,
    styledComponents: false,
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // SERVER OPTIONS
  // ─────────────────────────────────────────────────────────────────────────────

  poweredByHeader: false,
  trustHostHeader: true,

  // ─────────────────────────────────────────────────────────────────────────────
  // LOGGING
  // ─────────────────────────────────────────────────────────────────────────────

  logging: {
    fetches: {
      fullUrl: isDev,
      hmrRefreshes: isDev,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // ON DEMAND REVALIDATION
  // ─────────────────────────────────────────────────────────────────────────────

  onDemandEntries: {
    maxInactiveAge: 60 * 60 * 1000, // 1 hour
    pagesBufferLength: 10,
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORT CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

export default withBundleAnalyzer(nextConfig);
