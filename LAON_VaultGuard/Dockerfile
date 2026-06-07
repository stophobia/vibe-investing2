# LAON VaultGuard Docker image
# Multi-stage build: compile native deps → production runtime

# ── build stage (compiles better-sqlite3 native addon) ──
FROM node:20-alpine AS builder
RUN apk add --no-cache python3 make g++
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
# --omit=dev skips typescript/eslint, but better-sqlite3 is a prod dep

# ── runtime stage (minimal Alpine) ──
FROM node:20-alpine
RUN apk add --no-cache git
WORKDIR /app

# copy production node_modules (includes compiled better-sqlite3)
COPY --from=builder /app/node_modules ./node_modules

# copy source + config
COPY src/ ./src/
COPY public/ ./public/
COPY docs/ ./docs/
COPY package.json tsconfig.json ./

# data volume (repos, findings, vaultguard.db, logs)
RUN mkdir -p /app/data
VOLUME /app/data

# runtime config via env
ENV PORT=3101
ENV HOST=0.0.0.0
ENV DB_PATH=/app/data
ENV STORAGE_ENGINE=sqlite
ENV DP_ENABLED=true
ENV NODE_ENV=production

EXPOSE 3101

# health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3101/api/status || exit 1

CMD ["node", "--import=tsx", "src/index.ts"]
