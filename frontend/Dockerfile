# # Stage 1: Build
# FROM node:18-alpine AS builder
# WORKDIR /app

# COPY package*.json ./
# RUN npm install

# COPY . .
# RUN npm run build

# # Stage 2: Production Runner
# FROM node:18-alpine AS runner
# WORKDIR /app

# ENV NODE_ENV=production

# # Copy only necessary files
# COPY package*.json ./
# RUN npm install --omit=dev   # install only production deps

# COPY --from=builder /app/public ./public
# COPY --from=builder /app/.next ./.next

# EXPOSE 3001
# CMD ["npm", "start"]

# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install

# Copy project files (src, public, configs, etc.)
COPY . .

# Allow overriding API URLs at build time (falls back to .env values if not set)
ARG NEXT_PUBLIC_API_BASE_URL
ARG NEXT_PUBLIC_WEBSOCKET_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
ENV NEXT_PUBLIC_WEBSOCKET_URL=${NEXT_PUBLIC_WEBSOCKET_URL}

# Build Next.js app
RUN npm run build

# Stage 2: Production Runner
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Install only production dependencies
COPY package*.json ./
RUN npm install --omit=dev

# Copy build output and public assets from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 443
CMD ["npm", "start"]

