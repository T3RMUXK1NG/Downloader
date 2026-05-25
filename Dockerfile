# ═══════════════════════════════════════════════════════════════════════════════
# RS TOOLKIT v3.0.1 ULTIMATE NEXUS - Dockerfile
# ═══════════════════════════════════════════════════════════════════════════════
# Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
# License: OMNIPOTENT SOVEREIGN NEXUS
#
# Multi-stage production-ready Dockerfile with:
#   - Optimized build layers
#   - Security hardening
#   - Minimal final image size
#   - Health checks
#   - Non-root user execution
#   - Standalone output support
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1: Base image with common dependencies
# ─────────────────────────────────────────────────────────────────────────────

FROM node:20-alpine AS base

# Build arguments for versioning
ARG NODE_VERSION=20
ARG VERSION=3.0.1
ARG BUILD_DATE
ARG VCS_REF

# Labels for container metadata
LABEL maintainer="RAJSARASWATI JATAV (RS) - T3rmuxk1ng"
LABEL org.opencontainers.image.title="RS Toolkit"
LABEL org.opencontainers.image.description="Elite Security Toolkit - OMNIPOTENT SOVEREIGN NEXUS"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.vendor="T3rmuxk1ng"
LABEL org.opencontainers.image.licenses="OMNIPOTENT-SOVEREIGN-NEXUS"
LABEL org.opencontainers.image.source="https://github.com/T3rmuxk1ng/rs-toolkit"

# Install essential system dependencies
RUN apk add --no-cache \
    libc6-compat \
    python3 \
    py3-pip \
    ffmpeg \
    yt-dlp \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2: Dependencies installation
# ─────────────────────────────────────────────────────────────────────────────

FROM base AS deps

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies with cache optimization
RUN --mount=type=cache,target=/root/.npm \
    npm ci --prefer-offline --no-audit --ignore-scripts

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 3: Builder - Build the application
# ─────────────────────────────────────────────────────────────────────────────

FROM deps AS builder

# Copy source code
COPY . .

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV NEXT_BUILD_ID=${VERSION}

# Build the application
RUN --mount=type=cache,target=/app/.next/cache \
    npm run build

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 4: Production runner - Minimal production image
# ─────────────────────────────────────────────────────────────────────────────

FROM base AS runner

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs \
    && mkdir -p /app/data /app/logs \
    && chown -R nextjs:nodejs /app

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NEXT_PUBLIC_APP_VERSION=${VERSION}

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Copy Python scripts if they exist
COPY --chown=nextjs:nodejs ./core ./core 2>/dev/null || true
COPY --chown=nextjs:nodejs ./utils ./utils 2>/dev/null || true
COPY --chown=nextjs:nodejs ./modules ./modules 2>/dev/null || true
COPY --chown=nextjs:nodejs requirements.txt ./ 2>/dev/null || true

# Install Python dependencies if requirements.txt exists
RUN if [ -f requirements.txt ]; then \
    pip3 install --no-cache-dir -r requirements.txt --break-system-packages || true; \
    fi

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 5: Development runner (optional)
# ─────────────────────────────────────────────────────────────────────────────

FROM deps AS development

# Copy source code
COPY . .

# Set environment variables
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]

# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTION ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────

# Default to production runner
FROM runner AS production

# Set working directory
WORKDIR /app

# Start the application
CMD ["node", "server.js"]

# ─────────────────────────────────────────────────────────────────────────────
# ADDITIONAL BUILD TARGETS
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# TARGET: Full-featured image with all tools
# ─────────────────────────────────────────────────────────────────────────────

FROM runner AS full

USER root

# Install additional tools
RUN apk add --no-cache \
    curl \
    wget \
    git \
    ffmpeg \
    yt-dlp \
    streamlink \
    gallery-dl \
    aria2 \
    openssh-client \
    gnupg \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Install Node.js global tools
RUN npm install -g \
    pm2 \
    nodemon \
    serve \
    @anthropic-ai/claude-code

# Create directories
RUN mkdir -p /app/downloads /app/cache /app/logs \
    && chown -R nextjs:nodejs /app

USER nextjs

# Start with PM2 for process management
CMD ["pm2-runtime", "server.js"]

# ─────────────────────────────────────────────────────────────────────────────
# TARGET: Minimal image (smallest possible)
# ─────────────────────────────────────────────────────────────────────────────

FROM gcr.io/distroless/nodejs20-debian12 AS minimal

# Copy built application
COPY --from=builder --chown=1001:1001 /app/.next/standalone ./
COPY --from=builder --chown=1001:1001 /app/.next/static ./.next/static
COPY --from=builder --chown=1001:1001 /app/public ./public

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start server
CMD ["server.js"]

# ─────────────────────────────────────────────────────────────────────────────
# TARGET: Testing image
# ─────────────────────────────────────────────────────────────────────────────

FROM deps AS testing

# Copy source code
COPY . .

# Install testing dependencies
RUN npm install -D \
    vitest \
    @vitest/coverage-v8 \
    @testing-library/react \
    playwright

# Install Playwright browsers
RUN npx playwright install --with-deps chromium

# Set environment
ENV NODE_ENV=test

# Run tests
CMD ["npm", "run", "test:coverage"]

# ─────────────────────────────────────────────────────────────────────────────
# TARGET: Build-only image (for CI)
# ─────────────────────────────────────────────────────────────────────────────

FROM builder AS build-only

# Output the build artifacts
# Use: docker build --target build-only -o type=local,dest=./build .

# ─────────────────────────────────────────────────────────────────────────────
# TARGET: Python tools image
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim AS python-tools

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    aria2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python files
COPY requirements.txt ./
COPY ./core ./core
COPY ./utils ./utils
COPY ./modules ./modules
COPY rs_toolkit.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1001 rstoolkit \
    && chown -R rstoolkit:rstoolkit /app

USER rstoolkit

# Entry point
ENTRYPOINT ["python3", "rs_toolkit.py"]
CMD ["--help"]
