# API 错误码文档

Stream-Agent V9 所有微服务的统一错误码说明。

## 通用 HTTP 状态码

| 状态码 | 名称 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 202 | Accepted | 请求已接受，正在处理 |
| 204 | No Content | 请求成功，无返回内容 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或令牌无效 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 请求格式正确但语义错误 |
| 500 | Internal Server Error | 服务器内部错误 |

## Auth Service (8001)

### 400 Bad Request

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Email already registered` | 邮箱已被注册 | 使用其他邮箱或登录 |
| `Username already taken` | 用户名已被占用 | 使用其他用户名 |
| `Current password is incorrect` | 当前密码错误 | 检查密码是否正确 |
| `Password must contain at least one uppercase letter` | 密码缺少大写字母 | 添加大写字母 |
| `Password must contain at least one lowercase letter` | 密码缺少小写字母 | 添加小写字母 |
| `Password must contain at least one digit` | 密码缺少数字 | 添加数字 |
| `Username can only contain letters, numbers, and underscores` | 用户名格式错误 | 仅使用字母、数字、下划线 |

### 401 Unauthorized

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Invalid email or password` | 邮箱或密码错误 | 检查登录凭证 |
| `Invalid or expired token` | 令牌无效或已过期 | 重新登录获取新令牌 |
| `Invalid or expired refresh token` | 刷新令牌无效或已过期 | 重新登录 |
| `Invalid token payload` | 令牌载荷无效 | 重新登录获取新令牌 |
| `User not found` | 用户不存在 | 检查账户是否存在 |

### 403 Forbidden

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `User account is deactivated` | 账户已被禁用 | 联系管理员 |

## Chat Service (8002)

### 400 Bad Request

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Invalid conversation ID` | 会话 ID 格式错误 | 使用有效的 UUID |
| `Content cannot be empty` | 消息内容为空 | 提供消息内容 |

### 401 Unauthorized

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Not authenticated` | 未提供认证令牌 | 在请求头添加 Bearer Token |
| `Invalid token` | 令牌无效 | 重新登录获取新令牌 |

### 404 Not Found

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Conversation not found` | 会话不存在 | 检查会话 ID 是否正确 |
| `Message not found` | 消息不存在 | 检查消息 ID 是否正确 |

### 500 Internal Server Error

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Agent execution failed` | Agent 执行失败 | 检查 API 密钥配置 |
| `Tool execution failed` | 工具执行失败 | 检查工具配置和网络 |

## RAG Service (8004)

### 400 Bad Request

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Unsupported file type` | 不支持的文件类型 | 使用 .txt, .md, .pdf, .docx |
| `Failed to read file` | 文件读取失败 | 检查文件是否损坏 |
| `Failed to extract text from PDF` | PDF 文本提取失败 | PDF 可能是扫描件或加密 |
| `Text content cannot be empty` | 文本内容为空 | 提供非空文本 |

### 401 Unauthorized

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Not authenticated` | 未提供认证令牌 | 在请求头添加 Bearer Token |

### 404 Not Found

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Document not found` | 文档不存在 | 检查文档 ID 是否正确 |
| `Citation not found` | 引用不存在 | 检查 chunk_id 是否正确 |

### 500 Internal Server Error

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Search failed` | 检索失败 | 检查向量服务连接 |
| `Failed to delete document` | 删除文档失败 | 检查数据库连接 |

## Presentation Service (8005)

### 400 Bad Request

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Invalid presentation ID` | 演示文稿 ID 格式错误 | 使用有效的 UUID |
| `Invalid slide index` | 幻灯片索引超出范围 | 检查索引是否在有效范围内 |
| `Invalid position` | 插入位置无效 | 检查位置是否在有效范围内 |
| `Cannot delete the last slide` | 无法删除最后一张幻灯片 | 至少保留一张幻灯片 |

### 401 Unauthorized

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Not authenticated` | 未提供认证令牌 | 在请求头添加 Bearer Token |

### 404 Not Found

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Presentation not found` | 演示文稿不存在 | 检查 ID 是否正确 |
| `Layout type not found` | 布局类型不存在 | 使用有效的布局类型 |
| `Theme not found` | 主题不存在 | 使用有效的主题名称 |

### 500 Internal Server Error

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| `Failed to generate presentation` | 生成演示文稿失败 | 检查 AI 服务配置 |
| `Failed to regenerate slide` | 重新生成幻灯片失败 | 检查 AI 服务配置 |
| `Failed to export PPTX` | 导出 PPTX 失败 | 检查服务器资源 |
| `Failed to get random image` | 获取随机图片失败 | 检查图片服务配置 |

## 错误响应格式

所有错误响应都遵循以下 JSON 格式：

```json
{
  "detail": "错误信息描述"
}
```

对于验证错误 (422)，响应格式为：

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "错误信息",
      "type": "error_type"
    }
  ]
}
```

## 错误处理最佳实践

1. **检查状态码**: 首先检查 HTTP 状态码确定错误类型
2. **解析错误信息**: 读取 `detail` 字段获取具体错误原因
3. **令牌刷新**: 收到 401 错误时，尝试使用 refresh_token 刷新令牌
4. **重试机制**: 对于 500 错误，可以实现指数退避重试
5. **用户提示**: 将错误信息转换为用户友好的提示
