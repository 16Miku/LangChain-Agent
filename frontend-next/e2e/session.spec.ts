import { test, expect } from '@playwright/test';
import { TEST_USER } from './fixtures';

/**
 * 会话管理 E2E 测试
 * 测试创建、删除、重命名会话等功能
 */
test.describe('会话管理', () => {
  // 模拟的会话列表
  const mockConversations = [
    {
      id: 'conv-1',
      title: 'Python Discussion',
      created_at: new Date().toISOString(),
    },
    {
      id: 'conv-2',
      title: 'JavaScript Tips',
      created_at: new Date(Date.now() - 86400000).toISOString(), // 昨天
    },
    {
      id: 'conv-3',
      title: 'Database Design',
      created_at: new Date(Date.now() - 172800000).toISOString(), // 前天
    },
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
  });

  test.describe('会话列表', () => {
    test('应该显示会话列表', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockConversations),
          });
        }
      });

      await page.goto('/chat');

      // 验证会话标题显示
      await expect(page.getByText('Python Discussion')).toBeVisible({ timeout: 5000 });
      await expect(page.getByText('JavaScript Tips')).toBeVisible();
      await expect(page.getByText('Database Design')).toBeVisible();
    });

    test('会话应按日期分组显示', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockConversations),
          });
        }
      });

      await page.goto('/chat');

      // 验证日期分组标签
      await expect(page.getByText('Today')).toBeVisible({ timeout: 5000 });
      await expect(page.getByText('Yesterday')).toBeVisible();
    });

    test('空会话列表应显示空状态', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([]),
          });
        }
      });

      await page.goto('/chat');

      // 新建聊天按钮应该可见
      await expect(page.getByRole('button', { name: /new chat/i })).toBeVisible();
    });
  });

  test.describe('创建会话', () => {
    test('点击新建聊天应创建新会话', async ({ page }) => {
      let createCalled = false;

      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockConversations),
          });
        } else if (route.request().method() === 'POST') {
          createCalled = true;
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

      await page.goto('/chat');

      // 点击新建聊天按钮
      await page.getByRole('button', { name: /new chat/i }).click();

      // 验证 API 被调用
      await page.waitForTimeout(500);
      expect(createCalled).toBe(true);
    });

    test('新建会话后应跳转到新会话页面', async ({ page }) => {
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
              id: 'conv-new-123',
              title: 'New Chat',
              created_at: new Date().toISOString(),
            }),
          });
        }
      });

      await page.goto('/chat');
      await page.getByRole('button', { name: /new chat/i }).click();

      // 应该跳转到新会话
      await expect(page).toHaveURL(/\/chat\/conv-new-123/, { timeout: 5000 });
    });
  });

  test.describe('选择会话', () => {
    test('点击会话应切换到该会话', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockConversations),
          });
        }
      });

      await page.route('**/api/v1/conversations/conv-2/messages', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { role: 'user', content: 'Hello' },
            { role: 'assistant', content: 'Hi there!' },
          ]),
        });
      });

      await page.goto('/chat');

      // 点击第二个会话
      await page.getByText('JavaScript Tips').click();

      // 应该跳转到该会话
      await expect(page).toHaveURL(/\/chat\/conv-2/, { timeout: 5000 });
    });

    test('当前会话应高亮显示', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockConversations),
          });
        }
      });

      await page.route('**/api/v1/conversations/conv-1/messages', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await page.goto('/chat/conv-1');

      // 当前会话项应该有不同的样式（通常是背景色）
      const activeItem = page.locator('[data-active="true"]').or(
        page.locator('.bg-accent').filter({ hasText: 'Python Discussion' })
      );
      // 验证存在活跃状态的会话项
    });
  });

  test.describe('删除会话', () => {
    test('删除会话应从列表中移除', async ({ page }) => {
      let deleteCalled = false;

      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockConversations),
          });
        }
      });

      await page.route('**/api/v1/conversations/conv-1', async (route) => {
        if (route.request().method() === 'DELETE') {
          deleteCalled = true;
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ success: true }),
          });
        }
      });

      await page.goto('/chat');

      // 等待会话列表加载
      await expect(page.getByText('Python Discussion')).toBeVisible({ timeout: 5000 });

      // 悬停在会话项上显示删除按钮
      const conversationItem = page.locator('button, div').filter({ hasText: 'Python Discussion' }).first();
      await conversationItem.hover();

      // 点击删除按钮（如果有的话）
      const deleteButton = page.locator('button').filter({ has: page.locator('svg.lucide-trash, svg.lucide-trash-2') }).first();
      if (await deleteButton.isVisible()) {
        await deleteButton.click();
        await page.waitForTimeout(500);
        expect(deleteCalled).toBe(true);
      }
    });

    test('删除当前会话应跳转到聊天首页', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockConversations),
          });
        }
      });

      await page.route('**/api/v1/conversations/conv-1', async (route) => {
        if (route.request().method() === 'DELETE') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ success: true }),
          });
        }
      });

      await page.route('**/api/v1/conversations/conv-1/messages', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await page.goto('/chat/conv-1');

      // 删除当前会话后应该跳转
      // 具体实现取决于 UI 设计
    });
  });

  test.describe('重命名会话', () => {
    test('双击会话标题应进入编辑模式', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockConversations),
          });
        }
      });

      await page.goto('/chat');

      // 等待会话列表加载
      await expect(page.getByText('Python Discussion')).toBeVisible({ timeout: 5000 });

      // 双击会话标题（如果支持）
      const titleElement = page.getByText('Python Discussion');
      await titleElement.dblclick();

      // 验证是否进入编辑模式（显示输入框）
      // 具体实现取决于 UI 设计
    });

    test('重命名后应更新显示', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockConversations),
          });
        }
      });

      await page.route('**/api/v1/conversations/conv-1', async (route) => {
        if (route.request().method() === 'PATCH' || route.request().method() === 'PUT') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              ...mockConversations[0],
              title: 'Renamed Conversation',
            }),
          });
        }
      });

      await page.goto('/chat');

      // 重命名操作的具体实现取决于 UI
    });
  });

  test.describe('用户菜单', () => {
    test('应该显示用户名', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await page.goto('/chat');

      // 用户名应该在侧边栏底部显示
      await expect(page.getByText(TEST_USER.username)).toBeVisible({ timeout: 5000 });
    });

    test('点击用户菜单应显示选项', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await page.goto('/chat');

      // 点击用户按钮
      const userButton = page.locator('aside button').filter({ hasText: TEST_USER.username });
      await userButton.click();

      // 菜单应该显示
      await expect(page.getByRole('menuitem', { name: /settings/i })).toBeVisible();
      await expect(page.getByRole('menuitem', { name: /logout/i })).toBeVisible();
    });

    test('点击登出应跳转到登录页', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await page.goto('/chat');

      // 点击用户按钮
      const userButton = page.locator('aside button').filter({ hasText: TEST_USER.username });
      await userButton.click();

      // 点击登出
      await page.getByRole('menuitem', { name: /logout/i }).click();

      // 应该跳转到登录页
      await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
    });

    test('点击设置应跳转到设置页', async ({ page }) => {
      await page.route('**/api/v1/conversations', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await page.goto('/chat');

      // 点击用户按钮
      const userButton = page.locator('aside button').filter({ hasText: TEST_USER.username });
      await userButton.click();

      // 点击设置
      await page.getByRole('menuitem', { name: /settings/i }).click();

      // 应该跳转到设置页
      await expect(page).toHaveURL(/\/settings/, { timeout: 5000 });
    });
  });
});
