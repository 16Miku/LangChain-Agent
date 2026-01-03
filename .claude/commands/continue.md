按照 @Note/Plan-V9.md 继续开发：

1. 查看 Plan-V9.md 中当前阶段的待办任务
2. 选择下一个未完成的任务开始开发
3. 使用 context7 获取相关技术文档（如需要）
4. 编写代码实现功能
5. 编写自动化测试脚本
6. **自动运行测试**（使用 Python 完整路径）:
   ```bash
   cd backend/rag-service && A:/Anaconda/envs/My-Chat-LangChain/python.exe -m pytest tests/ -v --tb=short
   ```
7. 根据测试结果自动修复问题
8. 测试通过后，更新 Plan-V9.md 开发进度。生成中文 git 提交信息（用户手动提交）
9. 更新 .gitignore（如需要）

自动化规则：
- 使用 `A:/Anaconda/envs/My-Chat-LangChain/python.exe` 执行 Python 命令
- 测试失败时自动分析并修复
- 每个任务完成后更新 Todo 列表

开发规范：
- 中文注释和文档字符串
- 完整的类型注解
- 遵循 PEP 8 规范
