# SillyRAG Backend

一个基于 RAG (Retrieval-Augmented Generation) 的知识问答系统后端服务。

## 功能特性

- **文档管理**: 支持上传和处理 PDF、DOCX、TXT、Markdown 等多种格式文档
- **智能检索**: 支持向量搜索和全文检索两种检索方式
- **知识空间**: 用户可创建和管理多个独立的知识空间
- **AI 对话**: 基于 DeepSeek LLM 的智能问答
- **文档分块**: 自动将文档分割成合理的文本块
- **语音功能**: 支持语音识别 (ASR) 和语音合成 (TTS)
- **中文支持**: 内置 jieba 分词，优化中文检索效果

## 技术栈

- **框架**: FastAPI + Uvicorn
- **数据库**: PostgreSQL + pgvector (向量存储)
- **嵌入模型**: HuggingFace Transformers / sentence-transformers
- **LLM**: DeepSeek
- **ASR**: Sherpa-ONNX
- **TTS**: Edge-TTS
- **分词**: jieba
- **ORM**: SQLAlchemy (异步)

## 项目结构

```
sillyrag-backend/
├── server.py                 # 服务入口
├── src/
│   ├── main.py              # FastAPI 应用初始化
│   ├── api/                 # API 路由
│   │   ├── space.py         # 知识空间接口
│   │   ├── file.py          # 文件管理接口
│   │   ├── chunk.py         # 文档块接口
│   │   ├── chat.py          # 聊天对话接口
│   │   ├── user.py          # 用户接口
│   │   └── voice.py         # 语音接口
│   ├── dao/                 # 数据访问层
│   ├── dto/                 # 数据传输对象
│   ├── handler/             # 处理器
│   │   ├── partition/       # 文档分块处理器
│   │   ├── embedding/       # 向量化处理器
│   │   ├── chat/            # 聊天处理器
│   │   └── search/          # 检索处理器
│   ├── services/            # 业务逻辑层
│   ├── models/              # 数据模型
│   ├── core/                # 核心组件
│   │   └── llm/            # LLM 模型
│   ├── db/                  # 数据库配置
│   └── utils/               # 工具类
├── uploads/                 # 文件上传目录
├── .env                     # 环境变量配置
├── Dockerfile               # Docker 镜像
└── pyproject.toml          # 项目依赖
```

## 环境要求

- Python 3.11+
- PostgreSQL 14+ (需安装 pgvector 扩展)

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd sillyrag-backend
```

### 2. 配置环境变量

复制 `.env` 文件并填写数据库配置：

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myrag

UPLOAD_DIR=uploads
```

### 3. 安装依赖

使用 uv (推荐):

```bash
uv sync
```

或使用 pip:

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

确保 PostgreSQL 已安装并启用了 pgvector 扩展：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 运行服务

### 开发模式

```bash
python server.py
```

支持以下参数：

- `--host`: 监听地址 (默认: 127.0.0.1)
- `--port`: 监听端口 (默认: 8000)
- `--reload`: 自动重载 (默认: True)
- `--log_level`: 日志级别 (debug/info/warning/error/critical, 默认: info)

示例：

```bash
python server.py --host 0.0.0.0 --port 8080 --log_level debug
```

### Docker 部署

构建镜像：

```bash
docker build -t sillyrag-backend .
```

运行容器：

```bash
docker run -d -p 8000:8000 --env-file .env sillyrag-backend
```

## API 接口

所有接口统一使用 `/api` 前缀：

- `GET /api/spaces` - 获取知识空间列表
- `POST /api/spaces` - 创建知识空间
- `POST /api/files/upload` - 上传文档
- `POST /api/chat` - 对话问答
- `POST /api/voice/asr` - 语音识别
- `POST /api/voice/tts` - 语音合成

完整的 API 文档请访问: http://localhost:8000/docs

## 主要功能说明

### 文档处理流程

1. 用户上传文档 (PDF/DOCX/TXT/MD)
2. 文档自动分块处理
3. 文本块向量化存储
4. 支持检索和问答

### 检索方式

- **向量搜索**: 基于语义相似度的检索
- **全文检索**: 基于关键词的检索

### 语音功能

- **ASR (语音识别)**: 将语音转为文本
- **TTS (语音合成)**: 将文本转为语音

## 开发

运行测试：

```bash
pytest
```

代码格式：

```bash
# 安装开发依赖
pip install black ruff isort

# 格式化代码
black src/
ruff check src/ --fix
isort src/
```

## 许可证

MIT License
