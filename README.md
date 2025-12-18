# AI Console

AI Console 是一个集成了 Azure AI 服务的企业级应用平台，提供文档翻译、智能对话等功能。项目采用前后端分离架构，后端基于 FastAPI，前端使用 Streamlit。

## 🚀 最新功能

### 📚 智能文档翻译服务 (Document Translation)
新版翻译服务已迁移至后端 API，支持多种模式和文件格式：

- **支持格式**: `.docx`, `.xlsx`, `.pptx`, `.pdf`
- **双模引擎**:
  - **CLOUD 模式** (推荐): 基于 Azure Document Translation 服务。
    - ✅ 支持原样保留文档排版 (如 PPTX, PDF)。
    - ✅ 支持大文件和批量处理。
    - ⚠️ 需要配置 Azure Storage。
  - **LOCAL 模式**: 基于 Azure OpenAI (LLM) 的语义翻译。
    - ✅ 适合 `.docx`, `.xlsx`, `.pptx` 的精准语义翻译。
    - ❌ 暂不支持 PDF。

## 🛠 技术栈

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Streamlit
- **Database**: PostgreSQL (Citus 扩展)
- **Cache**: Redis
- **AI Services**: Azure OpenAI, Azure Document Translation, Azure Blob Storage
- **Infrastructure**: Docker, Docker Compose

## 🏁 快速开始

### 1. 环境准备
确保本地已安装 [Docker](https://www.docker.com/) 和 [Docker Compose](https://docs.docker.com/compose/)。

### 2. 配置环境变量
复制 `.env.example` (如果有) 或创建 `.env` 文件，填入以下必要信息：

```ini
# Security
SECRET_KEY=your_secret_key
ALGORITHM=HS256

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Azure OpenAI (LLM & Local Translation)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Document Translation (Cloud Translation)
AZURE_TRANSLATOR_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_TRANSLATOR_KEY=your_key
AZURE_TRANSLATOR_REGION=eastus

# Azure Storage (Required for Cloud Translation)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
```

### 3. 启动服务
```bash
docker-compose up -d --build
```

- **Backend API**: http://localhost:8000/docs
- **Frontend UI**: http://localhost:8501

## 🔌 API 接口文档

详细 API 文档请在服务启动后访问 Swagger UI: `http://localhost:8000/docs`

### 核心接口说明

#### 1. 文档翻译
**POST** `/api/doc-tools/translate/document`

上传文件并进行翻译，返回翻译后的文件流。

- **Parameters (Form Data)**:
  - `file`: (File, Required) 待翻译文件
  - `target_lang`: (String, Required) 目标语言代码 (如 `en`, `zh-Hans`, `ja`)
  - `mode`: (String, Optional) 翻译模式，默认为 `local`
    - `cloud`: 使用 Azure 文档翻译服务 (支持 PDF)
    - `local`: 使用 LLM 逐段翻译

#### 2. 文本翻译
**POST** `/api/doc-tools/translate/text`

使用 LLM 进行直接文本翻译。

- **Body (JSON)**:
  ```json
  {
    "text": "Hello world",
    "source_lang": "auto",
    "target_lang": "zh-Hans"
  }
  ```

## 📂 项目结构

```
AI_Console/
├── backend/            # FastAPI 后端应用
│   ├── app/
│   │   ├── api/        # 路由定义 (doc_tools.py, auth.py)
│   │   ├── services/   # 业务逻辑 (translator.py, azure_ai.py)
│   │   ├── schemas/    # Pydantic 数据模型
│   │   └── utils/      # 工具类 (doc_parsers.py)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/           # Streamlit 前端应用
├── docker-compose.yml
└── README.md
```
