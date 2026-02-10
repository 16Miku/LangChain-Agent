import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E 测试配置
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // 测试目录
  testDir: './e2e',

  // 测试文件匹配模式
  testMatch: '**/*.spec.ts',

  // 并行执行
  fullyParallel: true,

  // CI 环境下禁止 .only
  forbidOnly: !!process.env.CI,

  // 失败重试次数
  retries: process.env.CI ? 2 : 0,

  // 并行 worker 数量
  workers: process.env.CI ? 1 : undefined,

  // 测试报告
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],

  // 全局配置
  use: {
    // 基础 URL
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',

    // 收集失败测试的 trace
    trace: 'on-first-retry',

    // 截图
    screenshot: 'only-on-failure',

    // 视频录制
    video: 'on-first-retry',

    // 超时设置
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },

  // 全局超时
  timeout: 60000,

  // 期望超时
  expect: {
    timeout: 10000,
  },

  // 浏览器配置
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // 本地开发时自动启动前端服务
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: true,
    timeout: 120000,
  },
});
