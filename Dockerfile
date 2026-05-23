# 🔱 RS DOWNLOADER TOOLKIT - GOD MODE NEXUS DOCKERFILE
# Multi-stage build for minimal image size

# ============================================
# Stage 1: Python CLI Tool
# ============================================
FROM python:3.11-slim as python-base

LABEL maintainer="RS (T3rmuxk1ng)"
LABEL version="2.0.0"
LABEL description="RS Downloader Toolkit - GOD MODE NEXUS Edition"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    aria2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python files
COPY Downloader/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Downloader/ .

# Create downloads directory
RUN mkdir -p /downloads

# Set entry point
ENTRYPOINT ["python", "rs_toolkit.py"]

# ============================================
# Stage 2: Next.js Web Application
# ============================================
FROM node:20-alpine as web-builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Build the application
RUN npm run build

# ============================================
# Stage 3: Production Image
# ============================================
FROM node:20-alpine as production

WORKDIR /app

# Install yt-dlp and ffmpeg
RUN apk add --no-cache \
    python3 \
    py3-pip \
    ffmpeg \
    yt-dlp

# Copy built Next.js app
COPY --from=web-builder /app/.next ./.next
COPY --from=web-builder /app/public ./public
COPY --from=web-builder /app/package*.json ./
COPY --from=web-builder /app/node_modules ./node_modules

# Create downloads directory
RUN mkdir -p /app/downloads

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=production
ENV PORT=3000

# Start the application
CMD ["npm", "start"]
