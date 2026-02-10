import { test, expect } from '@playwright/test';
import { LoginPage, RegisterPage, TEST_USER } from './fixtures';

/**
 * 用户认证流程 E2E 测试
 */
test.describe('用户认证', () => {
  test.describe('登录页面', () => {
    test('应该正确显示登录表单', async ({ page }) => {
      await page.goto('/login');

      // 验证页面元素
      await expect(page.getByRole('heading', { name: /welcome back/i })).toBeVisible();
      await expect(page.locator('#email')).toBeVisible();
      await expect(page.locator('#password')).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /sign up/i })).toBeVisible();
    });

    test('空表单提交应显示错误', async ({ page }) => {
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.submit();

      const error = await loginPage.getErrorMessage();
      expect(error).toContain('Please enter email and password');
    });

    test('只填邮箱提交应显示错误', async ({ page }) => {
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.fillEmail('test@example.com');
      await loginPage.submit();

      const error = await loginPage.getErrorMessage();
      expect(error).toContain('Please enter email and password');
    });

    test('密码显示/隐藏切换应正常工作', async ({ page }) => {
      await page.goto('/login');

      const passwordInput = page.locator('#password');
      const toggleButton = page.locator('button').filter({ has: page.locator('svg.lucide-eye, svg.lucide-eye-off') });

      // 默认应该是密码类型
      await expect(passwordInput).toHaveAttribute('type', 'password');

      // 点击切换按钮
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'text');

      // 再次点击切换回密码类型
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('点击注册链接应跳转到注册页', async ({ page }) => {
      await page.goto('/login');
      await page.getByRole('link', { name: /sign up/i }).click();

      await expect(page).toHaveURL('/register');
    });

    test('登录成功应跳转到聊天页', async ({ page }) => {
      // Mock API 响应
      await page.route('**/api/v1/auth/login', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access_token: 'mock_token',
            token_type: 'bearer',
            user: {
              id: 'user-123',
              username: TEST_USER.username,
              email: TEST_USER.email,
            },
          }),
        });
      });

      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(TEST_USER.email, TEST_USER.password);

      // 等待跳转
      await expect(page).toHaveURL(/\/chat/);
    });

    test('登录失败应显示错误信息', async ({ page }) => {
      // Mock API 错误响应
      await page.route('**/api/v1/auth/login', async (route) => {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Invalid email or password',
          }),
        });
      });

      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login('wrong@example.com', 'wrongpassword');

      // 等待错误消息出现
      await expect(page.locator('.bg-destructive\\/10')).toBeVisible();
    });
  });

  test.describe('注册页面', () => {
    test('应该正确显示注册表单', async ({ page }) => {
      await page.goto('/register');

      await expect(page.getByRole('heading', { name: /create account/i })).toBeVisible();
      await expect(page.locator('#username')).toBeVisible();
      await expect(page.locator('#email')).toBeVisible();
      await expect(page.locator('#password')).toBeVisible();
      await expect(page.locator('#confirmPassword')).toBeVisible();
      await expect(page.getByRole('button', { name: /create account/i })).toBeVisible();
    });

    test('空表单提交应显示错误', async ({ page }) => {
      const registerPage = new RegisterPage(page);
      await registerPage.goto();
      await registerPage.submit();

      const error = await registerPage.getErrorMessage();
      expect(error).toContain('All fields are required');
    });

    test('用户名太短应显示错误', async ({ page }) => {
      const registerPage = new RegisterPage(page);
      await registerPage.goto();
      await registerPage.fillUsername('ab');
      await registerPage.fillEmail('test@example.com');
      await registerPage.fillPassword('password123');
      await registerPage.fillConfirmPassword('password123');
      await registerPage.submit();

      const error = await registerPage.getErrorMessage();
      expect(error).toContain('Username must be at least 3 characters');
    });

    test('密码太短应显示错误', async ({ page }) => {
      const registerPage = new RegisterPage(page);
      await registerPage.goto();
      await registerPage.fillUsername('testuser');
      await registerPage.fillEmail('test@example.com');
      await registerPage.fillPassword('short');
      await registerPage.fillConfirmPassword('short');
      await registerPage.submit();

      const error = await registerPage.getErrorMessage();
      expect(error).toContain('Password must be at least 8 characters');
    });

    test('密码不匹配应显示错误', async ({ page }) => {
      const registerPage = new RegisterPage(page);
      await registerPage.goto();
      await registerPage.fillUsername('testuser');
      await registerPage.fillEmail('test@example.com');
      await registerPage.fillPassword('password123');
      await registerPage.fillConfirmPassword('different123');
      await registerPage.submit();

      const error = await registerPage.getErrorMessage();
      expect(error).toContain('Passwords do not match');
    });

    test('无效邮箱应显示错误', async ({ page }) => {
      const registerPage = new RegisterPage(page);
      await registerPage.goto();
      await registerPage.fillUsername('testuser');
      await registerPage.fillEmail('invalid-email');
      await registerPage.fillPassword('password123');
      await registerPage.fillConfirmPassword('password123');
      await registerPage.submit();

      const error = await registerPage.getErrorMessage();
      expect(error).toContain('valid email');
    });

    test('点击登录链接应跳转到登录页', async ({ page }) => {
      await page.goto('/register');
      await page.getByRole('link', { name: /sign in/i }).click();

      await expect(page).toHaveURL('/login');
    });

    test('注册成功应跳转到聊天页', async ({ page }) => {
      // Mock API 响应
      await page.route('**/api/v1/auth/register', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access_token: 'mock_token',
            token_type: 'bearer',
            user: {
              id: 'user-123',
              username: 'newuser',
              email: 'newuser@example.com',
            },
          }),
        });
      });

      const registerPage = new RegisterPage(page);
      await registerPage.goto();
      await registerPage.register('newuser', 'newuser@example.com', 'password123');

      await expect(page).toHaveURL(/\/chat/);
    });
  });

  test.describe('认证状态', () => {
    test('未登录访问聊天页应跳转到登录页', async ({ page }) => {
      // 清除任何存储的认证状态
      await page.goto('/login');
      await page.evaluate(() => localStorage.clear());

      await page.goto('/chat');

      // 应该被重定向到登录页
      await expect(page).toHaveURL(/\/login/);
    });
  });
});
