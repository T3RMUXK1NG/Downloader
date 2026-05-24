# 🔱 RS DOWNLOADER TOOLKIT v2.1.0 - GOD MODE NEXUS DOCKERFILE
# Multi-stage build for minimal image size
# Author: RS (T3rmuxk1ng)

# ============================================
# Stage 1: Base Python CLI Tool
# ============================================
FROM python:3.12-slim as python-base

LABEL maintainer="RS (T3rmuxk1ng)"
LABEL version="2.1.0"
LABEL description="RS Downloader Toolkit - GOD MODE NEXUS Edition"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    aria2 \
    yt-dlp \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY modules/ ./modules/
COPY core/ ./core/
COPY utils/ ./utils/
COPY rs_toolkit.py .

# Create downloads directory
RUN mkdir -p /downloads

# Volume for downloads
VOLUME ["/downloads"]

# Set entry point
ENTRYPOINT ["python", "rs_toolkit.py"]

# ============================================
# Stage 2: Next.js Web Application Builder
# ============================================
FROM oven/bun:1 AS web-builder

WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source files
COPY . .

# Build the application
RUN bun run build

# ============================================
# Stage 3: Production Image
# ============================================
FROM oven/bun:1-slim AS production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ffmpeg \
    yt-dlp \
    && rm -rf /var/lib/apt/lists/*

# Copy built Next.js app
COPY --from=web-builder /app/.next ./.next
COPY --from=web-builder /app/public ./public
COPY --from=web-builder /app/package.json ./
COPY --from=web-builder /app/bun.lock* ./
COPY --from=web-builder /app/node_modules ./node_modules
COPY --from=web-builder /app/next.config.ts ./

# Create downloads directory
RUN mkdir -p /app/downloads

# Volume for downloads
VOLUME ["/app/downloads"]

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start the application
CMD ["bun", "run", "start"]
