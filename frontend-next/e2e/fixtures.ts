import { test as base, Page } from '@playwright/test';

/**
 * 测试用户凭据
 */
export const TEST_USER = {
  username: 'e2e_test_user',
  email: 'e2e_test@example.com',
  password: 'TestPassword123!',
};

/**
 * 扩展的测试 fixture
 */
export const test = base.extend<{
  authenticatedPage: Page;
}>({
  /**
   * 已登录状态的页面
   */
  authenticatedPage: async ({ page }, use) => {
    // 设置 mock 认证状态
    await page.goto('/login');

    // 注入 mock token 到 localStorage
    await page.evaluate((user) => {
      const mockToken = 'mock_jwt_token_for_e2e_testing';
      const mockUser = {
        id: 'test-user-id',
        username: user.username,
        email: user.email,
      };
      localStorage.setItem('auth-storage', JSON.stringify({
        state: {
          token: mockToken,
          user: mockUser,
          isAuthenticated: true,
        },
        version: 0,
      }));
    }, TEST_USER);

    await page.goto('/chat');
    await use(page);
  },
});

export { expect } from '@playwright/test';

/**
 * 页面对象：登录页
 */
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async fillEmail(email: string) {
    await this.page.locator('#email').fill(email);
  }

  async fillPassword(password: string) {
    await this.page.locator('#password').fill(password);
  }

  async submit() {
    await this.page.getByRole('button', { name: /sign in/i }).click();
  }

  async login(email: string, password: string) {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.submit();
  }

  async getErrorMessage() {
    return this.page.locator('.bg-destructive\\/10').textContent();
  }
}

/**
 * 页面对象：注册页
 */
export class RegisterPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/register');
  }

  async fillUsername(username: string) {
    await this.page.locator('#username').fill(username);
  }

  async fillEmail(email: string) {
    await this.page.locator('#email').fill(email);
  }

  async fillPassword(password: string) {
    await this.page.locator('#password').fill(password);
  }

  async fillConfirmPassword(password: string) {
    await this.page.locator('#confirmPassword').fill(password);
  }

  async submit() {
    await this.page.getByRole('button', { name: /create account/i }).click();
  }

  async register(username: string, email: string, password: string) {
    await this.fillUsername(username);
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.fillConfirmPassword(password);
    await this.submit();
  }

  async getErrorMessage() {
    return this.page.locator('.bg-destructive\\/10').textContent();
  }
}

/**
 * 页面对象：聊天页
 */
export class ChatPage {
  constructor(private page: Page) {}

  async goto(conversationId?: string) {
    if (conversationId) {
      await this.page.goto(`/chat/${conversationId}`);
    } else {
      await this.page.goto('/chat');
    }
  }

  async sendMessage(message: string) {
    const textarea = this.page.locator('textarea[placeholder*="Type your message"]');
    await textarea.fill(message);
    await this.page.getByRole('button').filter({ has: this.page.locator('svg.lucide-send') }).click();
  }

  async waitForResponse(timeout = 30000) {
    // 等待 AI 响应出现
    await this.page.waitForSelector('[data-role="assistant"]', { timeout });
  }

  async getLastAssistantMessage() {
    const messages = this.page.locator('[data-role="assistant"]');
    return messages.last().textContent();
  }

  async createNewChat() {
    await this.page.getByRole('button', { name: /new chat/i }).click();
  }

  async getConversationList() {
    return this.page.locator('[data-testid="conversation-item"]').all();
  }
}

/**
 * 页面对象：侧边栏
 */
export class Sidebar {
  constructor(private page: Page) {}

  async clickNewChat() {
    await this.page.getByRole('button', { name: /new chat/i }).click();
  }

  async selectConversation(title: string) {
    await this.page.getByText(title).click();
  }

  async deleteConversation(title: string) {
    const item = this.page.locator(`[data-testid="conversation-item"]:has-text("${title}")`);
    await item.hover();
    await item.getByRole('button', { name: /delete/i }).click();
  }

  async logout() {
    // 点击用户菜单
    await this.page.locator('aside button').filter({ hasText: /user/i }).click();
    await this.page.getByRole('menuitem', { name: /logout/i }).click();
  }
}
