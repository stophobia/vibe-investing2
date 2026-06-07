# LAON VaultGuard Docker image — Multi-stage (build → runtime)
#
# Stage 1: install all deps, esbuild bundle → dist/index.js
# Stage 2: production deps only, copy dist/ + src/ + public/ + docs/

# ── build stage ──
FROM node:20-alpine AS builder
RUN apk add --no-cache python3 make g++
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src/ ./src/
RUN npm run build

# ── runtime stage ──
FROM node:20-alpine
RUN apk add --no-cache git curl
WORKDIR /app

# production node_modules (includes compiled better-sqlite3 native addon)
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# built bundle (esbuild output)
COPY --from=builder /app/dist ./dist

# source modules (ESM imports from dist, but some modules need source at runtime for tsx CLI)
COPY src/ ./src/
COPY public/ ./public/
COPY docs/ ./docs/
COPY .env.example ./

# data volume
RUN mkdir -p /app/data
VOLUME /app/data

# runtime config
ENV PORT=3101
ENV HOST=0.0.0.0
ENV DB_PATH=/app/data
ENV STORAGE_ENGINE=sqlite
ENV DP_ENABLED=true
ENV NODE_ENV=production

EXPOSE 3101

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -sf http://localhost:3101/api/status || exit 1

CMD ["node", "dist/index.js"]
