# Anaconda → uv 迁移评估与依赖记录

> 日期: 2026-02-08
> 目的: 评估从 Anaconda 迁移到 uv 的可行性，并记录完整依赖

---

## 一、迁移可行性评估

### 1.1 结论：✅ 推荐迁移

| 评估项 | 结果 | 说明 |
|--------|------|------|
| **PyPI 兼容性** | ✅ 完全兼容 | 95% 的包来自 PyPI |
| **Conda 特有包** | ✅ 可替代 | 仅基础运行时来自 conda-forge |
| **性能提升** | ✅ 显著 | uv 比 pip 快 10-100 倍 |
| **磁盘占用** | ✅ 大幅减少 | 无需 conda 基础环境 |
| **项目隔离** | ✅ 更好 | 每个项目独立 .venv |

### 1.2 当前 Conda 环境分析

从 `conda list` 输出分析：

| 来源 | 包数量 | 占比 |
|------|--------|------|
| PyPI (`pypi_0`) | ~180 | 95% |
| conda-forge | ~10 | 5% |

**conda-forge 包清单（仅基础运行时）：**
- python 3.12.12
- pip, setuptools, wheel
- openssl, libffi, libsqlite, libzlib 等系统库

这些都可以通过 uv 的 Python 管理功能替代。

### 1.3 潜在风险与应对

| 风险 | 可能性 | 应对方案 |
|------|--------|----------|
| PyTorch/CUDA 兼容 | 低 | 当前使用 CPU 版本，无影响 |
| faster-whisper 依赖 | 低 | PyPI 版本可用 |
| 某些包版本不一致 | 中 | 使用 lock 文件锁定版本 |

---

## 二、完整依赖记录

### 2.1 Python 版本

```
Python 3.12.12
```

### 2.2 核心依赖（按实际安装版本）

以下是从 `conda list` 提取的完整 PyPI 依赖：

```txt
# ============================================================
# My-Chat-LangChain 完整依赖 (从 conda list 提取)
# Python 3.12.12
# 日期: 2026-02-08
# ============================================================

# === Web Framework ===
fastapi==0.116.1
uvicorn==0.35.0
starlette==0.47.3
python-multipart==0.0.20

# === Data Validation ===
pydantic==2.11.7
pydantic-core==2.33.2
pydantic-settings==2.12.0

# === Database ===
sqlalchemy==2.0.45
aiosqlite==0.21.0
psycopg2-binary==2.9.11
alembic==1.17.2
greenlet==3.3.0

# === Authentication ===
bcrypt==5.0.0
python-jose==3.5.0
passlib==1.7.4
cryptography==46.0.3

# === LangChain Ecosystem ===
langchain==0.3.27
langchain-community==0.3.29
langchain-core==0.3.76
langchain-google-genai==2.1.9
langchain-openai==0.3.33
langchain-huggingface==0.3.1
langchain-chroma==0.2.5
langchain-text-splitters==0.3.11
langchain-mcp-adapters==0.1.11

# === LangGraph ===
langgraph==0.6.6
langgraph-checkpoint==2.1.0
langgraph-checkpoint-sqlite==2.0.10
langgraph-prebuilt==0.6.5
langgraph-sdk==0.2.15
langsmith==0.3.45

# === Google AI ===
google-generativeai==0.8.6
google-genai==1.60.0
google-ai-generativelanguage==0.6.15
google-api-core==2.28.1
google-api-python-client==2.188.0
google-auth==2.47.0
google-auth-httplib2==0.3.0
googleapis-common-protos==1.72.0

# === OpenAI ===
openai==1.109.1
tiktoken==0.12.0

# === Vector Store & Embedding ===
chromadb==1.0.20
pymilvus==2.6.6
sentence-transformers==5.1.1
flashrank==0.2.10

# === ML/DL Core ===
torch==2.9.1
transformers==4.57.3
tokenizers==0.22.1
safetensors==0.7.0
huggingface-hub==0.36.0

# === Scientific Computing ===
numpy==2.3.5
scipy==1.16.3
pandas==2.3.3
scikit-learn==1.8.0

# === NLP ===
jieba==0.42.1

# === PDF Processing ===
pypdf==5.8.0
pypdf2==3.0.1

# === PPTX Generation ===
python-pptx==1.0.2
pillow==11.3.0

# === Speech (Whisper) ===
faster-whisper==1.2.1
ctranslate2==4.6.2
edge-tts==7.2.7
av==16.0.1

# === MCP (Model Context Protocol) ===
mcp==1.13.1
fastapi-mcp==0.4.0

# === E2B (Code Sandbox) ===
e2b==2.8.1
e2b-code-interpreter==2.4.1

# === HTTP Clients ===
httpx==0.28.1
httpx-sse==0.4.3
httpcore==1.0.9
requests==2.32.5
requests-oauthlib==2.0.0
requests-toolbelt==1.0.0
urllib3==2.3.0
aiohttp==3.13.2

# === Async ===
anyio==4.12.0
asyncio==1.3.0 (pytest-asyncio)
aiohappyeyeballs==2.6.1
aiosignal==1.4.0

# === Serialization ===
orjson==3.11.5
ormsgpack==1.12.1
protobuf==5.29.5
proto-plus==1.27.0

# === gRPC ===
grpcio==1.76.0
grpcio-status==1.71.2

# === Telemetry ===
opentelemetry-api==1.39.1
opentelemetry-sdk==1.39.1
opentelemetry-exporter-otlp-proto-common==1.39.1
opentelemetry-exporter-otlp-proto-grpc==1.39.1
opentelemetry-proto==1.39.1
opentelemetry-semantic-conventions==0.60b1

# === Web Scraping ===
beautifulsoup4==4.13.4
lxml==6.0.2
soupsieve==2.8

# === Playwright (Browser Automation) ===
playwright==1.57.0
pyee==13.0.0

# === Streamlit (Legacy Frontend) ===
streamlit==1.46.1
altair==5.5.0
pydeck==0.9.1
tornado==6.5.4
watchdog==6.0.0

# === Testing ===
pytest==9.0.2
pytest-asyncio==1.3.0

# === CLI & Utilities ===
click==8.3.1
typer==0.20.0
rich==14.2.0
colorama==0.4.6
tqdm==4.67.1
tabulate==0.9.0

# === Configuration ===
python-dotenv==1.1.1
pyyaml==6.0.3
toml==0.10.2

# === JSON Schema ===
jsonschema==4.25.1
jsonschema-specifications==2025.9.1
jsonpatch==1.33
jsonpointer==3.0.0

# === Data Classes ===
dataclasses-json==0.6.7
marshmallow==3.26.1
typing-extensions==4.15.0
typing-inspect==0.9.0

# === Networking ===
websockets==15.0.1
websocket-client==1.9.0
dnspython==2.8.0

# === Kubernetes (Optional) ===
kubernetes==34.1.0

# === Excel ===
xlsxwriter==3.2.9
pyarrow==22.0.0

# === Other Utilities ===
cachetools==6.2.4
filelock==3.20.1
filetype==1.2.0
fsspec==2025.12.0
jinja2==3.1.6
markupsafe==3.0.3
packaging==25.0
regex==2025.11.3
tenacity==9.1.2
xxhash==3.6.0
zstandard==0.23.0

# === Git ===
gitpython==3.1.45
gitdb==4.0.12
smmap==5.0.2

# === Analytics ===
posthog==5.4.0

# === ONNX Runtime ===
onnxruntime==1.23.2
flatbuffers==25.9.23

# === Misc ===
backoff==2.2.1
deprecated==1.2.18
email-validator==2.3.0
humanfriendly==10.0
joblib==1.5.3
markdown-it-py==4.0.0
mdurl==0.1.2
mmh3==5.2.0
mpmath==1.3.0
narwhals==2.14.0
networkx==3.6.1
overrides==7.7.0
pygments==2.19.2
pyparsing==3.3.2
pypika==0.48.9
pytz==2025.2
referencing==0.37.0
rpds-py==0.30.0
shellingham==1.5.4
six==1.17.0
sniffio==1.3.1
sympy==1.14.0
threadpoolctl==3.6.0
tzdata==2025.3
watchfiles==1.1.1
wcmatch==10.1
zipp==3.23.0
```

### 2.3 各服务依赖汇总

#### auth-service (端口 8001)
```txt
fastapi>=0.115.0
uvicorn>=0.30.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
aiosqlite>=0.20.0
bcrypt>=4.0.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.9
email-validator>=2.0.0
```

#### chat-service (端口 8002)
```txt
fastapi>=0.115.0
uvicorn>=0.30.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
aiosqlite>=0.20.0
python-jose[cryptography]>=3.3.0
langchain>=0.3.0
langchain-core>=0.3.0
langchain-google-genai>=2.0.0
langchain-openai>=0.2.0
langgraph>=0.2.0
langgraph-checkpoint>=2.0.0
langchain-mcp-adapters>=0.1.0
e2b-code-interpreter>=1.0.0
python-dotenv>=1.0.0
httpx>=0.27.0
python-multipart>=0.0.9
```

#### whisper-service (端口 8003)
```txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
faster-whisper>=1.0.0
edge-tts>=6.1.0
python-multipart>=0.0.9
```

#### rag-service (端口 8004)
```txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
python-multipart>=0.0.9
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9
alembic>=1.13.0
pymilvus>=2.4.0
sentence-transformers>=2.7.0
jieba>=0.42.1
PyPDF2>=3.0.0
python-jose[cryptography]>=3.3.0
pydantic-settings>=2.0.0
httpx>=0.27.0
python-dotenv>=1.0.0
google-generativeai>=0.8.0
```

#### presentation-service (端口 8005)
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
sqlalchemy==2.0.35
aiosqlite==0.20.0
asyncpg==0.29.0
pydantic==2.9.0
pydantic-settings==2.6.0
httpx==0.27.0
langchain-google-genai==2.0.5
langchain-core==0.3.14
e2b-code-interpreter==1.0.0
python-dotenv==1.0.1
python-pptx>=0.6.21
Pillow>=10.0.0
requests>=2.31.0
```

#### pptx-renderer-service (端口 8006) - V10 新增
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.9
pydantic>=2.0.0
pydantic-settings>=2.0.0
playwright>=1.40.0
python-pptx>=0.6.21
Pillow>=10.0.0
httpx>=0.25.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

### 2.4 前端依赖 (Node.js)

```json
{
  "dependencies": {
    "@radix-ui/react-avatar": "^1.1.11",
    "@radix-ui/react-dialog": "^1.1.15",
    "@radix-ui/react-dropdown-menu": "^2.1.16",
    "@radix-ui/react-scroll-area": "^1.2.10",
    "@radix-ui/react-select": "^2.2.6",
    "@radix-ui/react-separator": "^1.1.8",
    "@radix-ui/react-slot": "^1.2.4",
    "@radix-ui/react-tooltip": "^1.2.8",
    "axios": "^1.13.2",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.562.0",
    "next": "16.1.1",
    "react": "19.2.3",
    "react-dom": "19.2.3",
    "react-markdown": "^10.1.0",
    "rehype-highlight": "^7.0.2",
    "remark-gfm": "^4.0.1",
    "tailwind-merge": "^3.4.0",
    "zustand": "^5.0.9"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.1.1",
    "tailwindcss": "^4",
    "tw-animate-css": "^1.4.0",
    "typescript": "^5"
  }
}
```

---

## 三、uv 迁移步骤

### 3.1 安装 uv

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip (已安装)
pip install uv
```

### 3.2 创建项目配置

在项目根目录创建 `pyproject.toml`：

```toml
[project]
name = "my-chat-langchain"
version = "10.0.0"
description = "Stream-Agent - 全栈 AI 研究助理应用"
requires-python = ">=3.12"

[tool.uv]
python = "3.12"
```

### 3.3 迁移命令

```bash
# 1. 卸载 Anaconda 前，先导出环境
conda list --export > conda-packages-backup.txt

# 2. 创建 uv 虚拟环境
cd A:\study\AI\LLM\LangChain-Agent
uv venv .venv --python 3.12

# 3. 激活环境
.venv\Scripts\activate  # Windows

# 4. 安装依赖
uv pip install -r requirements-full.txt

# 5. 验证安装
python -c "import langchain; print(langchain.__version__)"
```

### 3.4 卸载 Anaconda

确认 uv 环境正常后：

```bash
# Windows
# 1. 控制面板 → 程序和功能 → 卸载 Anaconda
# 2. 删除残留目录
rmdir /s /q A:\Anaconda
rmdir /s /q %USERPROFILE%\.conda
rmdir /s /q %USERPROFILE%\.condarc
```

---

## 四、注意事项

### 4.1 特殊包处理

| 包 | 说明 | 处理方式 |
|---|------|----------|
| `torch` | 当前 CPU 版本 | `uv pip install torch` 即可 |
| `faster-whisper` | 依赖 ctranslate2 | PyPI 版本可用 |
| `playwright` | 需要安装浏览器 | `playwright install chromium` |

### 4.2 环境变量

迁移后需要更新：
- `PATH`: 移除 Anaconda 路径，添加 uv 路径
- `PYTHONPATH`: 如有设置需更新

### 4.3 IDE 配置

- VS Code: 更新 Python 解释器路径为 `.venv\Scripts\python.exe`
- PyCharm: 重新配置项目解释器

---

## 五、回滚方案

如果迁移失败，可以：

1. 重新安装 Anaconda
2. 使用备份的 `conda-packages-backup.txt` 恢复环境：
   ```bash
   conda create -n My-Chat-LangChain --file conda-packages-backup.txt
   ```

---

> **文档版本**: 1.0
> **最后更新**: 2026-02-08
