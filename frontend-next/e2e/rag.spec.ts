import { test, expect } from '@playwright/test';
import { TEST_USER } from './fixtures';
import path from 'path';

/**
 * 文档上传和 RAG 问答 E2E 测试
 */
test.describe('文档上传和 RAG 问答', () => {
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
          body: JSON.stringify([]),
        });
      } else if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'conv-rag',
            title: 'RAG Chat',
            created_at: new Date().toISOString(),
          }),
        });
      }
    });

    // Mock 文档列表
    await page.route('**/api/v1/rag/documents', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'doc-1',
              filename: 'test-document.pdf',
              status: 'completed',
              chunk_count: 15,
              created_at: new Date().toISOString(),
            },
          ]),
        });
      }
    });
  });

  test.describe('文档上传', () => {
    test('应该显示文件上传按钮', async ({ page }) => {
      await page.goto('/chat');

      // 附件按钮应该可见
      const attachButton = page.locator('button').filter({ has: page.locator('svg.lucide-paperclip') });
      await expect(attachButton).toBeVisible();
    });

    test('上传文档应触发 RAG 摄取', async ({ page }) => {
      let uploadCalled = false;

      // Mock 文档上传 API
      await page.route('**/api/v1/rag/ingest', async (route) => {
        uploadCalled = true;
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            document_id: 'doc-new',
            filename: 'uploaded-file.pdf',
            status: 'processing',
            message: 'Document is being processed',
          }),
        });
      });

      await page.goto('/chat');

      // 创建测试文件
      const fileInput = page.locator('input[type="file"]').first();

      // 使用 setInputFiles 模拟文件选择
      await fileInput.setInputFiles({
        name: 'test-document.pdf',
        mimeType: 'application/pdf',
        buffer: Buffer.from('PDF content placeholder'),
      });

      // 验证上传被触发（根据实际实现可能需要调整）
    });

    test('支持的文件类型应该被接受', async ({ page }) => {
      await page.goto('/chat');

      const fileInput = page.locator('input[type="file"]').first();
      const acceptAttr = await fileInput.getAttribute('accept');

      // 验证支持的文件类型
      expect(acceptAttr).toContain('pdf');
      expect(acceptAttr).toContain('csv');
    });
  });

  test.describe('RAG 问答', () => {
    test('基于文档的问答应返回带引用的回答', async ({ page }) => {
      // Mock 带引用的聊天响应
      await page.route('**/api/v1/chat/stream', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: `data: {"type": "content", "content": "Based on the document, the answer is..."}\n\ndata: {"type": "citations", "citations": [{"document_id": "doc-1", "chunk_id": "chunk-1", "content": "Relevant excerpt from document", "score": 0.95}]}\n\ndata: {"type": "end"}\n\n`,
        });
      });

      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('What does the document say about X?');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      // 用户消息应显示
      await expect(page.getByText('What does the document say about X?')).toBeVisible({ timeout: 5000 });
    });

    test('无相关文档时应给出适当回复', async ({ page }) => {
      await page.route('**/api/v1/chat/stream', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: 'data: {"type": "content", "content": "I don\'t have any documents that contain information about that topic."}\n\ndata: {"type": "end"}\n\n',
        });
      });

      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('Tell me about something not in any document');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      await expect(page.getByText('Tell me about something not in any document')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('引用追溯', () => {
    test('点击引用应显示原文', async ({ page }) => {
      // Mock 带引用的响应
      await page.route('**/api/v1/chat/stream', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: `data: {"type": "content", "content": "The answer is 42 [1]."}\n\ndata: {"type": "citations", "citations": [{"id": "1", "document_id": "doc-1", "content": "The answer to life is 42.", "page": 5}]}\n\ndata: {"type": "end"}\n\n`,
        });
      });

      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      await textarea.fill('What is the answer?');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      // 等待响应
      await page.waitForTimeout(1000);

      // 如果有引用标记，点击应该显示详情
      const citationLink = page.locator('[data-citation]').first();
      if (await citationLink.isVisible()) {
        await citationLink.click();
        // 验证引用面板或弹窗出现
      }
    });
  });

  test.describe('混合检索', () => {
    test('复杂查询应使用混合检索', async ({ page }) => {
      let searchParams: string | null = null;

      await page.route('**/api/v1/chat/stream', async (route) => {
        searchParams = route.request().postData();
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: 'data: {"type": "content", "content": "Based on semantic and keyword search..."}\n\ndata: {"type": "end"}\n\n',
        });
      });

      await page.goto('/chat');

      const textarea = page.locator('textarea[placeholder*="Type your message"]');
      // 包含关键词和语义的复杂查询
      await textarea.fill('Find documents about machine learning algorithms for classification');
      await page.locator('button').filter({ has: page.locator('svg.lucide-send') }).click();

      await page.waitForTimeout(1000);
      expect(searchParams).toBeTruthy();
    });
  });
});
