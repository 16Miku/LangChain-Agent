运行 RAG 服务测试：

1. 生成测试命令供用户执行：
   ```bash
   conda activate My-Chat-LangChain
   cd backend/rag-service
   python -m pytest tests/ -v --tb=short
   ```

2. 等待用户粘贴测试结果

3. 分析测试结果：
   - 如果全部通过：报告成功
   - 如果有失败：分析原因并提供修复方案

4. 如有修复，重新生成测试命令
