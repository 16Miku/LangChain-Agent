import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 输出模式: standalone 用于 Docker/云平台部署
  output: "standalone",

  // 环境变量
  // 注意: Windows 上使用 127.0.0.1 而不是 localhost，避免代理软件干扰
  env: {
    // 后端 API 地址 (客户端使用)
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8002",
    // Auth 服务地址
    NEXT_PUBLIC_AUTH_URL: process.env.NEXT_PUBLIC_AUTH_URL || "http://127.0.0.1:8001",
    // RAG 服务地址
    NEXT_PUBLIC_RAG_URL: process.env.NEXT_PUBLIC_RAG_URL || "http://127.0.0.1:8004",
    // Whisper 服务地址
    NEXT_PUBLIC_WHISPER_URL: process.env.NEXT_PUBLIC_WHISPER_URL || "http://127.0.0.1:8003",
    // Presentation 服务地址
    NEXT_PUBLIC_PRESENTATION_URL: process.env.NEXT_PUBLIC_PRESENTATION_URL || "http://127.0.0.1:8005",
  },

  // 图片域名白名单 (外部图片)
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },

  // 实验性功能
  experimental: {
    // 优化包大小
    optimizePackageImports: ["lucide-react", "@radix-ui/react-icons"],
  },

  // 禁用 x-powered-by 头 (安全)
  poweredByHeader: false,

  // 压缩
  compress: true,

  // API 代理 - 绕过浏览器代理，直接从 Next.js 服务端转发到后端
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8002";
    const authUrl = process.env.NEXT_PUBLIC_AUTH_URL || "http://127.0.0.1:8001";
    const ragUrl = process.env.NEXT_PUBLIC_RAG_URL || "http://127.0.0.1:8004";
    const whisperUrl = process.env.NEXT_PUBLIC_WHISPER_URL || "http://127.0.0.1:8003";
    const presentationUrl = process.env.NEXT_PUBLIC_PRESENTATION_URL || "http://127.0.0.1:8005";

    return [
      // Chat Service
      {
        source: "/api/chat/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
      // Auth Service
      {
        source: "/api/auth/:path*",
        destination: `${authUrl}/api/auth/:path*`,
      },
      // RAG Service
      {
        source: "/api/rag/:path*",
        destination: `${ragUrl}/api/:path*`,
      },
      // Whisper Service
      {
        source: "/api/whisper/:path*",
        destination: `${whisperUrl}/api/:path*`,
      },
      // Presentation Service
      {
        source: "/api/presentation/:path*",
        destination: `${presentationUrl}/api/:path*`,
      },
      {
        source: "/api/v1/:path*",
        destination: `${presentationUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
