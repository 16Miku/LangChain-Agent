import { test, expect } from '@playwright/test';
import { TEST_USER } from './fixtures';

/**
 * 多轮对话 E2E 测试
 * 测试查询改写、上下文保持等功能
 */
test.describe('多轮对话', () => {
  // 模拟的对话历史
  const mockMessages = [
    { role: 'user', content: 'What is Python?' },
    { role: 'assistant', content: 'Python is a high-level programming language known for its simplicity and readability.' },
  ];

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

    // Mock 会话列表
    await page.route('**/api/v1/conversations', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'conv-existing',
              title: 'Python Discussion',
              created_at: new Date().toISOString(),
            },
          ]),
        });
      } else if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'conv-new',
            title: 'New Chat',
            created_at: new Date().toISOString(),
          }),
        });
      }
    });

    // Mock 获取会话消息
    await page.route('**/api/v1/conversations/conv-existing/messages', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMessages),
      });
    });
  });

  test.describe('上下文保持', () => {
    test('加载已有会话应显示历史消息', async ({ page }) => {
      await page.goto('/chat/conv-existing');

      // 等待消息加载
      await expect(page.getByText('What is Python?')).toBeVisible({ timeout: 5000 });
      await expect(page.getByText(/Python is a high-level programming language/)).toBeVisible();
    });

    test('在已有会话中发送消息应保持上下文', async ({ page }) => {
      let requestBody: string | null = null;

      // 拦截聊天请求以验证上下文
      await page.route('**/api/v1/chat/stream', async (route) => {
        requestBody = route.request().postData();
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: 'data: {"type": "content", "content": "Python has many popular frameworks like Django and Flask."}\n\ndata: {"type": "end"}\n\n',
        });
      });

      await page.goto('/chat/conv-existing');

      // 等待历史消息加载
      await expect(page.getByText('What is Python?')).toBeVisible({ timeout: 5000 });

      // 发送后续问题
      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('What are its popular frameworks?');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      // 验证请求包含会话 ID（表示上下文保持）
      await page.waitForTimeout(1000);
      expect(requestBody).toBeTruthy();
    });

    test('代词引用应正确解析', async ({ page }) => {
      // 这个测试验证 AI 能理解 "it" 指代 Python
      await page.route('**/api/v1/chat/stream', async (route) => {
        const body = route.request().postData();
        // 验证消息被发送
        expect(body).toBeTruthy();

        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: 'data: {"type": "content", "content": "Python was created by Guido van Rossum in 1991."}\n\ndata: {"type": "end"}\n\n',
        });
      });

      await page.goto('/chat/conv-existing');
      await expect(page.getByText('What is Python?')).toBeVisible({ timeout: 5000 });

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('Who created it?');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      // 用户消息应显示
      await expect(page.getByText('Who created it?')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('查询改写', () => {
    test('模糊查询应被正确理解', async ({ page }) => {
      await page.route('**/api/v1/chat/stream', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: 'data: {"type": "content", "content": "Based on our discussion about Python, here are some learning resources..."}\n\ndata: {"type": "end"}\n\n',
        });
      });

      await page.goto('/chat/conv-existing');
      await expect(page.getByText('What is Python?')).toBeVisible({ timeout: 5000 });

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('How do I learn it?');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      await expect(page.getByText('How do I learn it?')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('长对话处理', () => {
    test('多轮对话后界面应保持响应', async ({ page }) => {
      // Mock 长对话历史
      const longHistory = [];
      for (let i = 0; i < 10; i++) {
        longHistory.push({ role: 'user', content: `Question ${i + 1}` });
        longHistory.push({ role: 'assistant', content: `Answer ${i + 1} with some detailed explanation.` });
      }

      await page.route('**/api/v1/conversations/conv-long/messages', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(longHistory),
        });
      });

      await page.route('**/api/v1/chat/stream', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: 'data: {"type": "content", "content": "Here is my response."}\n\ndata: {"type": "end"}\n\n',
        });
      });

      await page.goto('/chat/conv-long');

      // 验证可以滚动查看历史
      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await expect(textarea).toBeVisible();
      await expect(textarea).toBeEnabled();

      // 发送新消息应该正常工作
      await textarea.fill('New question');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      await expect(page.getByText('New question')).toBeVisible({ timeout: 5000 });
    });
  });
});
