# ============================================================
# Frontend Next.js Dockerfile
# ============================================================
# 多阶段构建，优化镜像大小
#
# 构建命令:
#   docker build -t frontend-next .
#
# 运行命令:
#   docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8002 frontend-next
# ============================================================

# ============================================================
# Stage 1: 依赖安装
# ============================================================
FROM node:20-alpine AS deps

WORKDIR /app

# 安装依赖
COPY package.json package-lock.json* ./
RUN npm ci --only=production=false

# ============================================================
# Stage 2: 构建
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 构建时环境变量 (可被运行时覆盖)
ARG NEXT_PUBLIC_API_URL=http://localhost:8002
ARG NEXT_PUBLIC_AUTH_URL=http://localhost:8001
ARG NEXT_PUBLIC_RAG_URL=http://localhost:8004
ARG NEXT_PUBLIC_WHISPER_URL=http://localhost:8003

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_AUTH_URL=$NEXT_PUBLIC_AUTH_URL
ENV NEXT_PUBLIC_RAG_URL=$NEXT_PUBLIC_RAG_URL
ENV NEXT_PUBLIC_WHISPER_URL=$NEXT_PUBLIC_WHISPER_URL

# 禁用 Next.js 遥测
ENV NEXT_TELEMETRY_DISABLED=1

# 构建
RUN npm run build

# ============================================================
# Stage 3: 运行
# ============================================================
FROM node:20-alpine AS runner

WORKDIR /app

# 创建非 root 用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 设置环境
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# 复制必要文件
COPY --from=builder /app/public ./public

# 设置正确的权限
RUN mkdir .next
RUN chown nextjs:nodejs .next

# 复制 standalone 输出
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 切换到非 root 用户
USER nextjs

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["node", "server.js"]
