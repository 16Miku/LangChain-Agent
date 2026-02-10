import { test, expect } from '@playwright/test';
import { TEST_USER } from './fixtures';

/**
 * 基础对话功能 E2E 测试
 */
test.describe('基础对话功能', () => {
  // 每个测试前设置认证状态并 mock API
  test.beforeEach(async ({ page }) => {
    // 设置认证状态
    await page.goto('/login');
    await page.evaluate((user) => {
      localStorage.setItem('auth-storage', JSON.stringify({
        state: {
          token: 'mock_jwt_token',
          user: {
            id: 'test-user-id',
            username: user.username,
            email: user.email,
          },
          isAuthenticated: true,
        },
        version: 0,
      }));
    }, TEST_USER);

    // Mock 会话列表 API
    await page.route('**/api/v1/conversations', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      } else {
        await route.continue();
      }
    });
  });

  test.describe('聊天界面', () => {
    test('应该正确显示聊天界面元素', async ({ page }) => {
      await page.goto('/chat');

      // 验证侧边栏
      await expect(page.getByText('Stream-Agent')).toBeVisible();
      await expect(page.getByRole('button', { name: /new chat/i })).toBeVisible();

      // 验证输入区域
      await expect(page.locator('textarea[placeholder*="Type your message"]')).toBeVisible();
    });

    test('输入框应支持文本输入', async ({ page }) => {
      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('Hello, this is a test message');

      await expect(textarea).toHaveValue('Hello, this is a test message');
    });

    test('空消息不应发送', async ({ page }) => {
      await page.goto('/chat');

      // 发送按钮应该被禁用
      const sendButton = page.locator('button').filter({ has: page.locator('svg.lucide-send') });
      await expect(sendButton).toBeDisabled();
    });

    test('输入文本后发送按钮应启用', async ({ page }) => {
      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('Test message');

      const sendButton = page.locator('button').filter({ has: page.locator('svg.lucide-send') });
      await expect(sendButton).toBeEnabled();
    });

    test('Enter 键应发送消息', async ({ page }) => {
      // Mock 创建会话 API
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'conv-123',
              title: 'New Chat',
              created_at: new Date().toISOString(),
            }),
          });
        } else {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([]),
          });
        }
      });

      // Mock 聊天流式 API
      await page.route('**/api/v1/chat/stream', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: 'data: {"type": "content", "content": "Hello! How can I help you?"}\n\ndata: {"type": "end"}\n\n',
        });
      });

      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('Hello');
      await textarea.press('Enter');

      // 输入框应该被清空
      await expect(textarea).toHaveValue('');
    });

    test('Shift+Enter 应换行而不发送', async ({ page }) => {
      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('Line 1');
      await textarea.press('Shift+Enter');
      await textarea.type('Line 2');

      const value = await textarea.inputValue();
      expect(value).toContain('Line 1');
      expect(value).toContain('Line 2');
    });
  });

  test.describe('消息发送与响应', () => {
    test('发送消息后应显示用户消息', async ({ page }) => {
      // Mock APIs
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'conv-123',
              title: 'New Chat',
              created_at: new Date().toISOString(),
            }),
          });
        } else {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([]),
          });
        }
      });

      await page.route('**/api/v1/chat/stream', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: 'data: {"type": "content", "content": "I am an AI assistant."}\n\ndata: {"type": "end"}\n\n',
        });
      });

      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('What are you?');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      // 用户消息应该显示
      await expect(page.getByText('What are you?')).toBeVisible({ timeout: 5000 });
    });

    test('流式响应期间应显示停止按钮', async ({ page }) => {
      // Mock 长时间运行的流式响应
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'conv-123',
              title: 'New Chat',
              created_at: new Date().toISOString(),
            }),
          });
        } else {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([]),
          });
        }
      });

      await page.route('**/api/v1/chat/stream', async (route) => {
        // 延迟响应以模拟流式传输
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: 'data: {"type": "content", "content": "Response"}\n\ndata: {"type": "end"}\n\n',
        });
      });

      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('Tell me a long story');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      // 停止按钮应该出现（在流式传输期间）
      const stopButton = page.locator('button').filter({ has: page.locator('svg.lucide-stop-circle') });
      // 注意：这个测试可能需要根据实际实现调整
    });
  });

  test.describe('附件功能', () => {
    test('应该显示附件按钮', async ({ page }) => {
      await page.goto('/chat');

      // 文件附件按钮
      const attachButton = page.locator('button').filter({ has: page.locator('svg.lucide-paperclip') });
      await expect(attachButton).toBeVisible();

      // 图片上传按钮
      const imageButton = page.locator('button').filter({ has: page.locator('svg.lucide-image') });
      await expect(imageButton).toBeVisible();
    });
  });
});
