# Plan-V10: 生产级优化与功能增强

> **版本**: V10.0
> **日期**: 2026-01-24 (更新: 2026-02-18)
> **目标**: 基于 V9 架构进行生产级优化，完善部署流程，增强 Agent 能力，优化 RAG 检索
> **状态**: 🚧 开发中

---

## ⚠️ 重要变更 (2026-02-18)

### V10 功能测试进度 (2026-02-18)

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 用户认证 (注册/登录) | ✅ 通过 | JWT 认证正常 |
| 基础对话 | ✅ 通过 | 流式响应正常 |
| 多轮对话 (查询改写) | ✅ 通过 | AI 正确理解指代词 |
| 工具调用 (网络搜索) | ✅ 通过 | search_engine 工具正常 |
| E2B 代码执行 | ✅ 通过 | 云沙箱正常创建和执行 |
| 演示文稿 | ⏭️ 跳过 | 保留功能，暂不测试 |
| RAG 文档问答 | ✅ 通过 | MinerU API 智能解析 |
| RAG 引用来源 UI | ✅ 通过 | 完整内容和位置显示 |

### Bug 修复记录 (2026-02-18)

| 问题 | 修复提交 | 说明 |
|------|---------|------|
| SQLite 数据库锁定 | - | 增加 timeout 和 pool_pre_ping |
| 历史对话重复加载 | - | 前端 selectConversation 添加防重复 |
| 对话重命名未保存 | - | handleRenameConversation 调用 API |
| 工具调用序列化错误 | c5ecdcf | tool_output 转字符串 |
| E2B API Key 读取失败 | c0a90ce | 从 settings 读取而非 os.environ |
| MinerU API URL 错误 | - | 使用官方 mineru.net/api/v4 |
| MinerU 批量查询端点错误 | - | 修正为 /extract-results/batch/{id} |
| MinerU 结果下载缺失 | - | 添加 zip 下载和 Markdown 提取 |
| 系统代理拦截请求 | - | httpx 添加 proxy=None |

### 放弃的模块
以下模块已决定放弃开发：
- ~~PPTX 导出升级~~ - HTML 预渲染机制
- ~~pptx-renderer-service~~ - 新服务
- ~~视觉验证系统~~
- ~~专业模板系统~~
- ~~动画效果支持~~

### 保留的核心目标
1. **部署流程完善**: Render + Supabase 云部署
2. **Agent 能力增强**: 工具并行调用、上下文压缩 (✅ 已完成)
3. **RAG 检索优化**: MinerU API、查询改写 (✅ 查询改写已完成)
4. **前端体验提升**: 移动端优化、E2E 测试

### 当前开发进度

| 模块 | 状态 | 说明 |
|------|------|------|
| ToolScheduler | ✅ 完成 | 工具调度器 |
| ContextCompressor | ✅ 完成 | 上下文压缩 |
| ToolCache | ✅ 完成 | 工具缓存 |
| QueryRewriterService | ✅ 完成 | 查询改写 |
| CI/CD 流水线 | ✅ 完成 | GitHub Actions |
| 部署脚本 | ✅ 完成 | deploy.sh |
| MinerU API 集成 | ✅ 完成 | vibe-kanban 并行 (2026-02-11) |
| 移动端适配 | ✅ 完成 | vibe-kanban 并行 (2026-02-11) |
| E2E 测试 | ✅ 完成 | vibe-kanban 并行 (2026-02-11) |
| API 文档完善 | ✅ 完成 | vibe-kanban 并行 (2026-02-11) |
| 代码审查修复 | ✅ 完成 | 后台任务 DB 会话问题 |

### vibe-kanban 并行任务完成记录 (2026-02-11)

| 任务 | 提交 | 变更文件数 | 新增代码行 |
|------|------|-----------|-----------|
| 移动端响应式适配 | 2cdc72a | 7 | +306/-140 |
| E2E 测试编写 | d03aaea | 11 | +1718 |
| API 文档完善 | 6840d1e | 11 | +994/-79 |
| MinerU API 集成 | f3f75d1 | 4 | +1382/-39 |

### 代码审查发现的问题及修复 (2026-02-11)

| 问题 | 严重程度 | 状态 |
|------|---------|------|
| 后台任务使用已关闭的 DB 会话 | 高 | ✅ 已修复 |
| 无效 Tailwind 类名 `size-default` | 高 | ✅ 已修复 |
| E2E 测试使用 waitForTimeout 反模式 | 中 | 待修复 |
| httpx.AsyncClient 未复用 | 中 | 待修复 |

### 新发现的 Bug (2026-02-18)

| 问题 | 严重程度 | 状态 | 说明 |
|------|---------|------|------|
| 未登录状态跳转异常 | 高 | ✅ 已修复 | 未登录时访问 / 自动跳转到 /chat 并显示上次登录用户名 |
| RAG 引用来源 UI 简陋 | 中 | ✅ 已修复 | 引用来源模块重新设计，完整内容和位置显示 |

#### Bug 详情

**1. 未登录状态跳转异常** ✅ 已修复
- **症状**: 清除 Cookie/LocalStorage 后访问 `http://localhost:3000/` 自动跳转到 `/chat`
- **表现**: 显示上次登录用户的姓名，但没有对话历史数据
- **原因**:
  - `authStore.ts` 使用 zustand persist 持久化 `user` 对象
  - `initialize()` 只检查 token，但 `user` 从 persist 恢复
  - `Sidebar.tsx` 只检查 `user` 存在就显示用户名，未检查 `isAuthenticated`
- **修复**:
  - `authStore.ts`: initialize 时清除残留 user
  - `AuthProvider.tsx`: 同步清除 user
  - `Sidebar.tsx`: 添加 isAuthenticated 检查

**2. RAG 引用来源 UI 简陋**
- **症状**: 文档问答的引用来源显示过于简单
- **当前状态**: 仅显示基础文本信息
- **期望**: 卡片式设计、来源文档标题、页码、高亮原文片段、可点击跳转

---

## 📑 目录

1. [版本概述](#一版本概述)
2. [V9 回顾与问题分析](#二v9-回顾与问题分析)
3. [V10 需求规格说明](#三v10-需求规格说明)
4. [系统架构优化](#四系统架构优化)
5. [模块详细设计](#五模块详细设计)
6. [开发计划](#六开发计划)
7. [风险评估与应对](#七风险评估与应对)
8. [验收标准](#八验收标准)
9. [附录](#九附录)

---

## 一、版本概述

### 1.1 版本目标

V10.0 是 My-Chat-LangChain 项目的**生产级优化版本**，核心目标是：

1. **PPTX 导出升级**: 引入 HTML 预渲染机制，达到商用级美学质量
2. **部署流程完善**: 完成 Render + Supabase 云部署，提供一键部署脚本
3. **Agent 能力增强**: 工具调用并行化、上下文压缩、多轮对话优化
4. **RAG 检索优化**: MinerU API 集成、查询改写、多轮对话检索
5. **前端体验提升**: 移动端优化、PWA 支持、性能优化

### 1.2 版本对比

```
V9.0 (当前)                              V10.0 (目标)
├── PPTX 导出 (2/10 美学评分)             ├── PPTX 导出 (8/10 商用级)
├── 本地开发为主                          ├── 云端部署完善 (Render + Supabase)
├── 基础 Agent 工具调用                   ├── 并行工具调用 + 上下文压缩
├── 混合检索 (向量+BM25)                  ├── 混合检索 + MinerU + 查询改写
├── 桌面端优先                            ├── 响应式 + PWA 支持
├── 手动文档解析                          ├── MinerU 智能文档解析
└── 172 项测试                            └── 200+ 项测试 + E2E 测试
```

### 1.3 核心功能清单

| 功能模块 | 子功能 | 优先级 | 阶段 |
|---------|--------|--------|------|
| **PPTX 导出升级** | HTML 预渲染机制 | P0 | Phase 1 |
| | 视觉验证系统 | P0 | Phase 1 |
| | 专业模板系统 | P1 | Phase 1 |
| | 动画效果支持 | P2 | Phase 2 |
| **部署完善** | Render 部署脚本 | P0 | Phase 1 |
| | Supabase 迁移工具 | P0 | Phase 1 |
| | CI/CD 流水线 | P1 | Phase 1 |
| | 监控告警系统 | P2 | Phase 2 |
| **Agent 增强** | 工具并行调用 | P0 | Phase 2 |
| | 上下文压缩 | P1 | Phase 2 |
| | 工具调用缓存 | P2 | Phase 2 |
| **RAG 优化** | MinerU API 集成 | P1 | Phase 2 |
| | 查询改写 (Query Rewriting) | P1 | Phase 2 |
| | 多轮对话检索 | P2 | Phase 3 |
| **前端优化** | 移动端适配 | P1 | Phase 3 |
| | PWA 支持 | P2 | Phase 3 |
| | 性能优化 (Lighthouse 90+) | P1 | Phase 3 |

---

## 二、V9 回顾与问题分析

### 2.1 V9 已完成功能

| 阶段 | 功能 | 状态 | 测试覆盖 |
|------|------|------|----------|
| Phase 1 | Next.js 前端重构 | ✅ 完成 | - |
| Phase 1 | 用户认证系统 (JWT) | ✅ 完成 | - |
| Phase 1 | 会话管理 | ✅ 完成 | - |
| Phase 2 | 图片理解 (多模态) | ✅ 完成 | - |
| Phase 2 | 语音交互 (Whisper + Edge TTS) | ✅ 完成 | - |
| Phase 3 | RAG 混合检索 | ✅ 完成 | 11 项测试 |
| Phase 3 | 引用追溯 | ✅ 完成 | - |
| Phase 3 | 文档目录提取 | ✅ 完成 | - |
| Phase 5 | AI 生成 PPT (Reveal.js) | ✅ 完成 | 172 项测试 |
| Phase 5 | 17 种主题系统 | ✅ 完成 | 40 项测试 |
| Phase 5 | 19 种布局引擎 | ✅ 完成 | 42 项测试 |
| Phase 5 | AI 对话式修改 | ✅ 完成 | 14 项测试 |
| Phase 5 | HTML 导出 | ✅ 完成 | 34 项测试 |

### 2.2 V9 遗留问题

#### 2.2.1 PPTX 导出质量问题 (严重 - P0)

**问题描述**: 当前 PPTX 导出功能美学评分仅 2/10，不可用于商用。

**根本原因分析**:

| 问题 | 原因 | 影响 |
|------|------|------|
| 空间滥用 | 硬编码位置，无内容感知 | 大量无意义空白 |
| 缺乏层次 | 所有元素平铺 | 无主次之分 |
| 装饰空洞 | 只有简单线条 | 缺乏设计感 |
| 色彩单一 | 纯色填充 | 无渐变、阴影、质感 |
| 排版僵硬 | 固定位置 | 无法适应不同内容 |

**技术架构层面的根本问题**:

1. **缺乏视觉反馈机制** - python-pptx 无法预览渲染效果
2. **与 pptx-skills 的本质差距** - 缺少"视觉验证"环节
3. **设计理念缺失** - 只关注功能实现，没有美学设计

#### 2.2.2 部署流程未完善 (中等 - P1)

| 问题 | 状态 |
|------|------|
| Render 部署配置 | ✅ render.yaml 已创建 |
| Supabase Schema | ✅ 已设计 |
| 实际部署测试 | ❌ 未执行 |
| CI/CD 流水线 | ❌ 未配置 |
| 环境变量管理 | ⚠️ 部分完成 |

#### 2.2.3 其他待优化项

| 问题 | 优先级 | 说明 |
|------|--------|------|
| MinerU API 未集成 | P1 | 智能文档解析 |
| 多轮对话检索 | P2 | 查询改写优化 |
| 移动端适配 | P2 | 响应式布局不完善 |
| 工具调用串行 | P1 | 影响响应速度 |

### 2.3 V9 技术债务

```
技术债务清单:
├── presentation-service
│   ├── PPTX 导出需要重构 (引入预渲染)
│   └── 图片服务需要更可靠的源 (Picsum 不稳定)
├── rag-service
│   ├── MinerU API 集成待完成
│   └── 多轮对话检索待优化
├── chat-service
│   ├── 工具调用并行化
│   └── 上下文压缩机制
├── frontend-next
│   ├── 移动端适配
│   └── PWA 支持
└── 部署
    ├── E2E 测试覆盖
    └── CI/CD 流水线
```

---

## 三、V10 需求规格说明

### 3.1 功能需求

#### 3.1.1 PPTX 导出升级 (FR-01)

**FR-01-01: HTML 预渲染机制**

参考 pptx-skills 的实现方式，引入 HTML 预渲染流程：

```
当前流程 (V9):
  AI 生成内容 → 硬编码位置 → python-pptx 生成 → PPTX 文件

目标流程 (V10):
  AI 生成内容 → HTML/CSS 渲染 → 浏览器截图/位置提取 → python-pptx 生成 → PPTX 文件
```

- 使用 Playwright/Puppeteer 进行 HTML 渲染
- 提取精确的元素位置和尺寸
- 支持渐变、阴影、圆角等 CSS 效果
- 复杂元素光栅化为图片嵌入

**FR-01-02: 视觉验证系统**

- 生成 PPTX 后自动截图预览
- 检测文字溢出、元素重叠
- 提供美学评分 (基于规则或 AI)
- 支持人工审核反馈

**FR-01-03: 专业模板系统**

- 提供 10+ 专业设计模板
- 支持模板自定义和导入
- 模板包含：配色、字体、布局、装饰元素
- 支持企业品牌定制

**FR-01-04: 动画效果支持**

- 入场动画 (淡入、滑入、缩放)
- 强调动画 (脉冲、摇摆)
- 退场动画
- 幻灯片切换效果

#### 3.1.2 部署完善 (FR-02)

**FR-02-01: Render 部署脚本**

- 一键部署脚本 (`deploy.sh`)
- 自动创建 Render 服务
- 环境变量自动配置
- 健康检查验证

**FR-02-02: Supabase 迁移工具**

- 数据库 Schema 自动迁移
- pgvector 扩展自动启用
- 初始数据导入
- 备份恢复工具

**FR-02-03: CI/CD 流水线**

```yaml
# .github/workflows/deploy.yml
触发条件:
  - push to main
  - pull request

流水线步骤:
  1. 代码检查 (lint)
  2. 单元测试
  3. 构建镜像
  4. E2E 测试
  5. 部署到 Render (仅 main)
```

**FR-02-04: 监控告警系统**

- 服务健康监控
- 错误日志聚合
- 性能指标收集
- 告警通知 (邮件/Slack)

#### 3.1.3 Agent 能力增强 (FR-03)

**FR-03-01: 工具并行调用**

当前问题：工具串行执行，响应慢

```python
# 当前 (V9) - 串行
result1 = await tool1.invoke(args1)
result2 = await tool2.invoke(args2)
result3 = await tool3.invoke(args3)

# 目标 (V10) - 并行
results = await asyncio.gather(
    tool1.invoke(args1),
    tool2.invoke(args2),
    tool3.invoke(args3)
)
```

- 识别可并行的工具调用
- 依赖分析和调度
- 并行执行结果合并
- 错误处理和回退

**FR-03-02: 上下文压缩**

- 长对话历史自动摘要
- 保留关键信息，压缩冗余
- 动态调整上下文窗口
- 支持多种压缩策略

**FR-03-03: 工具调用缓存**

- 相同参数的工具调用缓存
- 缓存过期策略
- 缓存命中率统计
- 支持手动清除缓存

#### 3.1.4 RAG 检索优化 (FR-04)

**FR-04-01: MinerU API 集成**

- 调用 MinerU 云服务 API
- 支持 PDF/Word/PPT 等格式
- 智能分块 (语义切分)
- 表格/图表/公式提取

**FR-04-02: 查询改写 (Query Rewriting)**

```
用户输入: "刚才说的那个方法具体怎么实现？"

查询改写后: "RAG 混合检索的 RRF 融合算法具体实现方式"
```

- 基于对话历史理解指代
- 补充隐含的上下文信息
- 生成更精确的检索查询
- 支持多查询扩展

**FR-04-03: 多轮对话检索**

- 对话历史上下文理解
- 追问场景优化
- 检索结果去重
- 相关性衰减机制

#### 3.1.5 前端优化 (FR-05)

**FR-05-01: 移动端适配**

- 响应式布局优化
- 触摸交互优化
- 移动端专属 UI 组件
- 手势支持 (滑动、缩放)

**FR-05-02: PWA 支持**

- Service Worker 离线缓存
- 添加到主屏幕
- 推送通知
- 后台同步

**FR-05-03: 性能优化**

- Lighthouse 评分 90+
- 首屏加载 < 1.5s
- 代码分割和懒加载
- 图片优化 (WebP, 懒加载)

### 3.2 非功能需求

#### 3.2.1 性能需求 (NFR-01)

| 指标 | V9 现状 | V10 目标 |
|------|---------|----------|
| 首屏加载时间 | < 2s | < 1.5s |
| 消息发送响应 | < 500ms | < 300ms |
| 流式首 Token | < 1s | < 800ms |
| RAG 检索延迟 | < 500ms | < 300ms |
| PPTX 生成 (10页) | ~10s | < 5s |
| 并发用户数 | 100+ | 500+ |

#### 3.2.2 可用性需求 (NFR-02)

| 指标 | 目标 |
|------|------|
| 服务可用性 | > 99.5% |
| 平均故障恢复时间 | < 5 分钟 |
| 数据备份频率 | 每日 |
| 灾难恢复时间 | < 1 小时 |

#### 3.2.3 安全需求 (NFR-03)

- HTTPS 强制启用
- JWT Token 定期轮换
- API 请求限流
- SQL 注入防护
- XSS 防护
- CORS 严格配置
- 敏感数据加密存储

#### 3.2.4 可维护性需求 (NFR-04)

| 指标 | 目标 |
|------|------|
| 单元测试覆盖率 | > 70% |
| E2E 测试覆盖 | 核心流程 100% |
| API 文档完整性 | 100% |
| 代码注释率 | > 30% |

---

## 四、系统架构优化

### 4.1 V10 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        My-Chat-LangChain V10.0                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Frontend (Next.js 14 + PWA)                      │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────────┐    │   │
│  │  │ Chat Page │ │ PPT Editor│ │ Documents │ │ Settings + Mobile │    │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  shadcn/ui + Tailwind + Service Worker (PWA)                │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                          HTTP/REST + SSE                                    │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Render Cloud (计算层)                             │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │   │
│  │  │ auth-service  │  │ chat-service  │  │ rag-service   │            │   │
│  │  │ Port: 8001    │  │ Port: 8002    │  │ Port: 8004    │            │   │
│  │  │ - JWT 认证    │  │ - LangGraph   │  │ - 混合检索    │            │   │
│  │  │ - 用户管理    │  │ - 并行工具    │  │ - MinerU      │            │   │
│  │  │               │  │ - 上下文压缩  │  │ - 查询改写    │            │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘            │   │
│  │                                                                      │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │   │
│  │  │ presentation  │  │ whisper       │  │ pptx-renderer │ ← NEW      │   │
│  │  │ -service      │  │ -service      │  │ (Playwright)  │            │   │
│  │  │ Port: 8005    │  │ Port: 8003    │  │ Port: 8006    │            │   │
│  │  │ - AI 生成 PPT │  │ - 语音识别    │  │ - HTML 预渲染 │            │   │
│  │  │ - 主题/布局   │  │ - TTS 合成    │  │ - 视觉验证    │            │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Supabase (数据层)                                 │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  PostgreSQL + pgvector                                       │    │   │
│  │  │  - users, conversations, messages                            │    │   │
│  │  │  - documents, document_chunks (vector)                       │    │   │
│  │  │  - presentations, slide_versions                             │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  Supabase Storage (文件存储)                                 │    │   │
│  │  │  - 上传的文档 (PDF, Word, PPT)                               │    │   │
│  │  │  - 生成的 PPTX 文件                                          │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    External Services                                 │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐   │   │
│  │  │ Gemini  │ │  E2B    │ │  MCP    │ │ MinerU  │ │ Unsplash    │   │   │
│  │  │ API     │ │ Sandbox │ │ Tools   │ │  API    │ │ API         │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 新增服务: pptx-renderer

V10 新增 `pptx-renderer` 服务，专门负责 HTML 预渲染和 PPTX 生成：

```
pptx-renderer-service/
├── app/
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 配置管理
│   ├── api/v1/
│   │   ├── render.py           # 渲染 API
│   │   └── validate.py         # 验证 API
│   └── services/
│       ├── html_renderer.py    # HTML 渲染服务 (Playwright)
│       ├── position_extractor.py # 位置提取服务
│       ├── pptx_generator.py   # PPTX 生成服务
│       └── visual_validator.py # 视觉验证服务
├── templates/                  # HTML 模板
│   ├── slide_base.html
│   └── layouts/
├── requirements.txt
└── Dockerfile
```

### 4.3 PPTX 生成流程 (V10)

```
presentation-service          pptx-renderer-service
┌─────────────────┐          ┌─────────────────────────┐
│ 1. AI 生成内容   │          │                         │
│    (幻灯片结构)  │          │                         │
└────────┬────────┘          │                         │
         │ POST /render       │                         │
         ├───────────────────►│ 2. HTML 渲染            │
         │                    │    (Playwright)         │
         │                    │ 3. 位置提取             │
         │                    │ 4. PPTX 生成            │
         │                    │ 5. 视觉验证             │
         │◄───────────────────┤                         │
         │ PPTX + 验证结果    │                         │
┌────────▼────────┐          └─────────────────────────┘
│ 6. 返回给前端   │
└─────────────────┘
```

### 4.4 数据库 Schema 优化

```sql
-- 模板表 (V10 新增)
CREATE TABLE pptx_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),  -- business, academic, creative
    thumbnail TEXT,
    config JSONB NOT NULL,
    is_system BOOLEAN DEFAULT false,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 工具调用缓存表 (V10 新增)
CREATE TABLE tool_call_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_name VARCHAR(100) NOT NULL,
    args_hash VARCHAR(64) NOT NULL,
    result JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tool_name, args_hash)
);

-- 查询改写历史表 (V10 新增)
CREATE TABLE query_rewrites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    original_query TEXT NOT NULL,
    rewritten_query TEXT NOT NULL,
    context_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 五、模块详细设计

### 5.1 pptx-renderer 服务设计

#### 5.1.1 HTML 渲染服务

```python
# app/services/html_renderer.py
from playwright.async_api import async_playwright

class HtmlRendererService:
    """使用 Playwright 渲染 HTML 幻灯片"""

    async def render_slide(self, slide_html: str, width: int = 1920, height: int = 1080) -> dict:
        """渲染单个幻灯片，返回截图和元素位置"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": width, "height": height})
            await page.set_content(slide_html)
            screenshot = await page.screenshot(type="png")
            elements = await self._extract_elements(page)
            await browser.close()
            return {"screenshot": screenshot, "elements": elements}
```

#### 5.1.2 视觉验证服务

```python
# app/services/visual_validator.py
class VisualValidatorService:
    """PPTX 视觉验证服务"""

    def validate(self, pptx_bytes: bytes, expected_screenshots: list) -> dict:
        """验证生成的 PPTX 与预期效果的一致性"""
        # 返回: {"score": 0.95, "issues": [...], "passed": True}
        pass
```

### 5.2 Agent 并行工具调用设计

```python
# app/services/tool_scheduler.py
class ToolScheduler:
    """工具调用调度器 - 分析依赖并并行执行"""

    async def execute_parallel(self, tool_calls: list) -> list:
        """并行执行无依赖的工具调用"""
        groups = self.analyze_dependencies(tool_calls)
        results = []
        for group in groups["parallel_groups"]:
            group_results = await asyncio.gather(*[
                self._execute_tool(call) for call in group
            ])
            results.extend(group_results)
        return results
```

### 5.3 RAG 查询改写设计

```python
# app/services/query_rewriter.py
class QueryRewriterService:
    """查询改写服务 - 基于对话历史优化检索查询"""

    async def rewrite(self, query: str, conversation_history: list) -> dict:
        """改写用户查询，解析指代词，补充上下文"""
        # 返回: {"main_query": "...", "variants": [...], "reasoning": "..."}
        pass
```

---

## 六、开发计划

### 6.1 阶段划分

```
Phase 1: PPTX 导出升级 + 部署完善 (3 周)
├── Week 1: pptx-renderer 服务开发
├── Week 2: 视觉验证 + 模板系统
└── Week 3: Render 部署 + CI/CD

Phase 2: Agent 增强 + RAG 优化 (2 周)
├── Week 4: 工具并行调用 + 上下文压缩
└── Week 5: MinerU 集成 + 查询改写

Phase 3: 前端优化 + 测试完善 (2 周)
├── Week 6: 移动端适配 + PWA
└── Week 7: E2E 测试 + 性能优化

Phase 4: 文档 + 发布 (1 周)
└── Week 8: 文档完善 + 版本发布
```

### 6.2 里程碑

| 里程碑 | 完成条件 | 预计日期 |
|--------|---------|----------|
| **M1: PPTX 商用级** | 美学评分 ≥ 8/10 | Week 2 |
| **M2: 云端部署** | Render + Supabase 上线 | Week 3 |
| **M3: Agent 增强** | 并行工具 + 压缩完成 | Week 4 |
| **M4: RAG 优化** | MinerU + 查询改写完成 | Week 5 |
| **M5: 前端优化** | PWA + 移动端完成 | Week 6 |
| **M6: V10 发布** | 所有测试通过 | Week 8 |

### 6.3 详细任务清单

#### Phase 1: PPTX 导出升级 + 部署完善

**Week 1: pptx-renderer 服务**
- [ ] 创建 pptx-renderer-service 项目结构
- [ ] 实现 HtmlRendererService (Playwright)
- [ ] 实现 PositionExtractorService
- [ ] 实现 PptxGeneratorService
- [ ] 编写单元测试

**Week 2: 视觉验证 + 模板系统**
- [ ] 实现 VisualValidatorService
- [ ] 创建 10+ 专业模板
- [ ] 模板管理 API
- [ ] 美学评分测试

**Week 3: 部署完善**
- [ ] 完善 render.yaml 配置
- [ ] 编写部署脚本 (deploy.sh)
- [ ] GitHub Actions CI/CD
- [ ] 部署测试验证

#### Phase 2: Agent 增强 + RAG 优化

**Week 4: Agent 增强**
- [ ] 实现 ToolScheduler
- [ ] 实现并行工具执行
- [ ] 实现 ContextCompressor
- [ ] 实现工具调用缓存

**Week 5: RAG 优化**
- [ ] MinerU API 集成
- [ ] 实现 QueryRewriterService
- [ ] 多轮对话检索优化

#### Phase 3: 前端优化

**Week 6-7: 移动端 + PWA + 测试**
- [ ] 响应式布局优化
- [ ] Service Worker 实现
- [ ] E2E 测试 (Playwright)
- [ ] Lighthouse 优化

---

## 七、风险评估与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| Playwright 云端部署困难 | 中 | 高 | 使用 Render Docker 部署 |
| MinerU API 不稳定 | 中 | 中 | 保留 PyPDF2 作为 fallback |
| 并行工具调用复杂度高 | 中 | 中 | 渐进式实现 |

---

## 八、验收标准

| 功能 | 验收条件 |
|------|----------|
| **PPTX 导出** | 美学评分 ≥ 8/10 |
| **云端部署** | Render 一键部署成功 |
| **工具并行** | 3 个独立工具并行执行 |
| **PWA** | Lighthouse PWA 评分 > 90 |

---

## 九、附录

### 9.1 参考资料

| 资源 | 链接 |
|------|------|
| Playwright 文档 | https://playwright.dev/python/ |
| MinerU API | https://github.com/opendatalab/MinerU |
| Unsplash API | https://unsplash.com/developers |

### 9.2 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| 1.0 | 2026-01-24 | 初始版本 | Claude Code |

---

> **文档状态**: 📋 规划中
> **最后更新**: 2026-01-24
