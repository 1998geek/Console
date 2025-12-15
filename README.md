# 🚀 AIPortal - Enterprise AI Services Platform

> 企业级 AI 服务平台，集成文档翻译、智能对话、文档审查等多种 AI 功能

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-latest-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## 📋 项目简介

AIPortal (ComLan) 是一个功能丰富的企业 AI 服务平台，提供：

- 🌐 **多语言文档翻译** - 支持 8 种语言的文本和文档翻译
- 💬 **智能对话系统** - 多模型 AI 对话，支持流式输出
- 📄 **文档智能审查** - 合同和标书的 AI 分析
- 🔍 **智能搜索** - 基于 Azure AI Search 的向量搜索
- 📊 **数据分析** - 智能问数和 BI 查询
- 🎨 **双界面架构** - Streamlit UI + FastAPI REST API

---

## ✨ 核心特性

### 🎯 双轨道架构

```
Streamlit UI (内部使用)  ←──┐
                           ├──→ 共享业务逻辑 (function/)
FastAPI (对外集成)       ←──┘
```

**优势**:
- 内部团队使用友好的 Streamlit UI
- 外部系统通过 REST API 集成
- 代码复用，避免重复开发

### 🔐 FastAPI REST API

完整的 REST API 实现，包括：
- JWT 认证系统
- 自动生成的 Swagger/ReDoc 文档
- 异步处理长时间任务
- 类型安全的 Pydantic 模型
- Docker 容器化支持

**查看**: [API 文档](./docs/)

---

## 🚀 快速开始

### 方法 1: 本地 Dev Container（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/ComlanOfficial/AI_Portal.git
cd AI_Portal

# 2. 在 VS Code 中打开
code .

# 3. 在 Dev Container 中重新打开
# F1 → "Dev Containers: Reopen in Container"

# 4. 启动服务
./start_dev.sh
```

**详细指南**: [本地开发环境设置](./docs/LOCAL_DEVCONTAINER_SETUP.md)

### 方法 2: 直接运行

```bash
# 安装依赖
pip install -r requirements_api.txt

# 启动 FastAPI
uvicorn api.main:app --reload

# 启动 Streamlit (可选)
streamlit run streamlit_app.py
```

### 访问服务

- **FastAPI Swagger UI**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501

---

## 📚 文档导航

完整文档位于 [`docs/`](./docs/) 目录：

### 🎯 快速入门
- [快速开始指南](./docs/QUICK_START.md) - 5 分钟快速上手 ⭐
- [开发快速参考](./docs/DEV_QUICKREF.md) - 常用命令和快捷键

### 📘 完整文档
- [API 项目说明](./docs/API_README.md) - FastAPI 项目总览
- [API 使用指南](./docs/API_USAGE_GUIDE.md) - 完整的 API 使用文档
- [本地开发设置](./docs/LOCAL_DEVCONTAINER_SETUP.md) - Dev Container 完整配置
- [API 架构设计](./docs/api_design.md) - 技术选型和架构说明

### 📖 文档中心
👉 **[查看完整文档索引](./docs/README.md)**

---

## 🎯 主要功能

### 1. 文档翻译
- 支持 8 种语言：中文（简/繁）、英语、日语、韩语、法语、德语、西班牙语
- 文档格式：Word、Excel、PowerPoint、PDF、TXT
- 云端翻译（Azure）+ 本地模型

### 2. 智能对话
- 多模型支持：GPT-4、Claude、Gemini
- 流式输出
- 多模态（文本 + 图像）
- 对话历史管理

### 3. 文档审查
- 合同智能初审：风险识别、建议生成
- 标书智能审查：合规性检查、完整性评分
- 文档对比：差异分析、相似度评分

### 4. 其他功能
- 案例查询
- 客户背景调研
- 售后问题助手
- 智能问数（Text-to-SQL）
- 员工违规操作识别

---

## 🏗️ 项目结构

```
AI_Portal/
├── 📁 api/                      # FastAPI 应用
│   ├── main.py                 # FastAPI 入口
│   ├── core/                   # 核心配置
│   │   ├── config.py          # 配置管理
│   │   └── security.py        # JWT 认证
│   ├── routes/                 # API 路由
│   │   ├── auth.py            # 认证
│   │   ├── translate.py       # 翻译
│   │   ├── chat.py            # 对话
│   │   └── review.py          # 文档审查
│   ├── models/                 # Pydantic 模型
│   ├── services/               # 业务逻辑
│   └── utils/                  # 工具函数
│
├── 📁 function/                 # 共享业务逻辑
│   ├── AzureAIClient.py
│   ├── AzureDocumentTranslator.py
│   └── ...
│
├── 📁 sub_pages/                # Streamlit 页面
│   ├── page_translate.py
│   ├── page_chat.py
│   └── ...
│
├── 📁 docs/                     # 文档目录 ⭐
│   ├── README.md               # 文档索引
│   ├── QUICK_START.md          # 快速开始
│   ├── API_USAGE_GUIDE.md      # API 使用指南
│   └── ...
│
├── 📁 .devcontainer/            # Dev Container 配置
├── 📁 .vscode/                  # VS Code 配置
│
├── 🐍 streamlit_app.py         # Streamlit 入口
├── 🚀 start_dev.sh             # 启动脚本
├── 🧪 test_api.py              # API 测试
└── 📄 requirements_api.txt     # API 依赖
```

---

## 🔧 技术栈

### 后端
- **FastAPI** - 现代化 Web 框架
- **Pydantic** - 数据验证
- **JWT** - 身份认证
- **Uvicorn** - ASGI 服务器

### 前端
- **Streamlit** - 快速构建 Web UI

### AI & 云服务
- **Azure OpenAI** - AI 服务
- **Azure AI Search** - 智能搜索
- **Azure Document Translation** - 文档翻译
- **Azure Storage** - 云存储

### 数据库
- **PostgreSQL** - 关系数据库

### 开发工具
- **Docker** - 容器化
- **VS Code Dev Containers** - 开发环境
- **Git** - 版本控制

---

## 📊 API 端点

### 认证
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 Token
- `GET /api/v1/auth/me` - 获取用户信息

### 翻译
- `POST /api/v1/translate/text` - 文本翻译
- `POST /api/v1/translate/document` - 文档翻译
- `GET /api/v1/translate/status/{task_id}` - 查询状态
- `GET /api/v1/translate/languages` - 支持的语言

### 对话
- `POST /api/v1/chat/completion` - AI 对话
- `POST /api/v1/chat/stream` - 流式对话
- `POST /api/v1/chat/multimodal` - 多模态对话
- `GET /api/v1/chat/models` - 可用模型

### 文档审查
- `POST /api/v1/review/contract` - 合同审查
- `POST /api/v1/review/bidding` - 标书审查
- `POST /api/v1/review/compare` - 文档对比

**完整 API 文档**: http://localhost:8000/docs

---

## 🧪 测试

### 运行 API 测试
```bash
python test_api.py
```

### 使用 REST Client
打开 `api_test.http` 文件，使用 VS Code REST Client 扩展测试

### 测试账号
```
管理员: admin / admin123
用户:   user / user123
```

---

## 🐳 Docker 部署

```bash
# FastAPI
docker-compose -f docker-compose.api.yml up

# 或使用 Dockerfile
docker build -f Dockerfile.api -t aiportal-api .
docker run -p 8000:8000 aiportal-api
```

---

## 🤝 贡献

欢迎贡献！请查看我们的贡献指南。

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🔗 相关链接

- **GitHub 仓库**: https://github.com/ComlanOfficial/AI_Portal
- **Issue 追踪**: https://github.com/ComlanOfficial/AI_Portal/issues
- **Pull Requests**: https://github.com/ComlanOfficial/AI_Portal/pulls

---

## 📞 联系我们

有问题或建议？欢迎提 Issue 或 Pull Request！

---

## 🎉 快速开始

```bash
# 1. 克隆并进入项目
git clone https://github.com/ComlanOfficial/AI_Portal.git && cd AI_Portal

# 2. 阅读快速开始指南
cat docs/QUICK_START.md

# 3. 启动服务
./start_dev.sh

# 4. 访问 API 文档
open http://localhost:8000/docs
```

**祝你使用愉快！** 🚀
