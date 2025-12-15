# 🔐 环境变量配置指南

本文档说明 AIPortal API 支持的所有环境变量配置。

---

## 📋 配置文件

环境变量通过 `.env` 文件加载，该文件应放在项目根目录。

```bash
# 项目结构
AI_Portal/
├── .env          ← 环境变量配置文件（不要提交到 Git）
├── api/
└── ...
```

---

## 🔧 基础配置

### 应用设置

```bash
# 应用名称
APP_NAME="AIPortal API"

# 应用版本
APP_VERSION="1.0.0"

# 调试模式 (true/false)
DEBUG=true

# API 路由前缀
API_V1_PREFIX="/api/v1"
```

---

## 🔐 安全配置

### JWT 认证

```bash
# JWT 密钥（生产环境必须修改！）
SECRET_KEY="your-super-secret-key-change-in-production"

# JWT 算法
ALGORITHM="HS256"

# Access Token 过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24小时

# Refresh Token 过期时间（天）
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ 安全提示**:
- 生产环境务必使用强密码作为 `SECRET_KEY`
- 可以用以下命令生成随机密钥：
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

---

## 🌐 CORS 配置

```bash
# 允许的跨域来源（逗号分隔）
CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"

# 或允许所有（开发环境）
CORS_ORIGINS="*"
```

---

## 💾 数据库配置

### PostgreSQL

```bash
# 方法 1: 使用完整连接字符串
DATABASE_URL="postgresql://user:password@localhost:5432/aiportal"

# 方法 2: 使用单独的配置项
DATABASE_HOST="localhost"
DATABASE_PORT="5432"
DATABASE_NAME="aiportal"
DATABASE_USER="your_user"
DATABASE_PASSWORD="your_password"
```

**支持的数据库**:
- PostgreSQL（推荐）
- MySQL
- SQLite

---

## ☁️ Azure 服务配置

### Azure Storage

```bash
# 连接字符串
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
AZURE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..."

# 或使用单独配置
AZURE_STORAGE_ENDPOINT="https://youraccount.blob.core.windows.net/"
AZURE_STORAGE_ACCOUNT_NAME="youraccount"
AZURE_STORAGE_KEY="your_storage_key"
AZURE_STORAGE_CONTAINER_NAME="translatecontainer"
AZURE_TARGET_CONTAINER_NAME="translatedcontainer"
```

### Azure AI Search

```bash
AZURE_SEARCH_ENDPOINT="https://your-search.search.windows.net"
AZURE_SEARCH_KEY="your_search_key"
```

### Azure OpenAI

```bash
AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com"
AZURE_OPENAI_KEY="your_openai_key"
AZURE_OPENAI_TOKEN="your_token"
AZURE_GROK3_REST_ENDPOINT="https://your-grok3.services.ai.azure.com"
```

### Azure Document Translation

```bash
AZURE_DOCUMENT_TRANSLATION_ENDPOINT="https://your-translator.cognitiveservices.azure.com/"
AZURE_DOCUMENT_TRANSLATION_KEY="your_translation_key"
```

---

## 🤖 AI 服务配置

### OpenAI

```bash
OPENAI_API_KEY="sk-your-openai-api-key"
```

### XInference（本地模型）

```bash
XINFERENCE_BASE_URL="http://localhost:9998/v1"
XINFERENCE_TRANSLATE_MODEL_NAME="qwen3"
```

### Aliyun AI

```bash
ALIYUN_AI_ENDPOINT="https://dashscope.aliyun.com/compatible-mode/v1"
ALIYUN_AI_TOKEN="sk-your-aliyun-token"
```

### Dify

```bash
# 默认 Dify API
DIFY_API_BASE_URL_DEFAULT="https://dify.yourdomain.com/v1"
DIFY_API_KEY_DEFAULT="app-your-dify-key"

# 案例研究 Dify API
DIFY_API_CASE_STUDY_URL="https://dify.yourdomain.com/v1"
DIFY_API_CASE_STUDY_KEY="app-your-case-study-key"
```

---

## 📧 邮件配置

### SMTP 设置

```bash
# 发件人邮箱
SENDER_USERNAME="your-email@domain.com"
SENDER_PASSWORD="your_email_password"

# SMTP 服务器
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"

# 收件人（逗号分隔多个）
TO_ADDRS="user1@domain.com,user2@domain.com"

# 发件人别名
FROM_ALIAS="AI Portal"
```

**常见 SMTP 服务器**:

| 服务商 | SMTP 地址 | 端口 | 安全 |
|--------|----------|------|------|
| Gmail | smtp.gmail.com | 587 | TLS |
| Outlook | smtp-mail.outlook.com | 587 | TLS |
| QQ | smtp.qq.com | 587 | TLS |
| 163 | smtp.163.com | 465 | SSL |

---

## 📰 RSS 配置

```bash
RSS_URL="https://news.example.com/rss.xml"
```

---

## 📤 文件上传配置

```bash
# 最大上传大小（字节）
MAX_UPLOAD_SIZE=52428800  # 50MB

# 上传目录
UPLOAD_DIR="/tmp/uploads"

# 允许的文件扩展名（代码中配置）
# .pdf, .docx, .pptx, .xlsx, .txt
```

---

## 🔄 任务队列配置

### Celery + Redis

```bash
CELERY_BROKER_URL="redis://localhost:6379/0"
CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

---

## 📝 .env 文件示例

### 开发环境

```bash
# .env.development
DEBUG=true
SECRET_KEY="dev-secret-key-for-testing-only"

# 数据库
DATABASE_URL="postgresql://user:password@localhost:5432/aiportal_dev"

# OpenAI
OPENAI_API_KEY="sk-your-dev-key"

# CORS - 允许本地开发
CORS_ORIGINS="http://localhost:3000,http://localhost:8501"
```

### 生产环境

```bash
# .env.production
DEBUG=false
SECRET_KEY="super-strong-random-secret-key-production"

# 数据库
DATABASE_URL="postgresql://user:password@prod-db:5432/aiportal"

# Azure 服务
AZURE_OPENAI_ENDPOINT="https://prod-openai.openai.azure.com"
AZURE_OPENAI_KEY="prod-key"

# CORS - 只允许生产域名
CORS_ORIGINS="https://yourdomain.com,https://api.yourdomain.com"
```

---

## 🔒 安全最佳实践

### 1. 不要提交 .env 文件到 Git

```bash
# .gitignore 中应包含
.env
.env.*
!.env.example
```

### 2. 使用 .env.example 作为模板

```bash
# .env.example（可以提交到 Git）
SECRET_KEY="change-me-in-production"
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
OPENAI_API_KEY="your-api-key-here"
```

### 3. 环境分离

```bash
# 不同环境使用不同的 .env 文件
.env.development
.env.staging
.env.production
```

### 4. 生产环境使用密钥管理服务

- **Azure Key Vault**
- **AWS Secrets Manager**
- **HashiCorp Vault**

---

## 🧪 验证配置

### 方法 1: Python 脚本

```python
from api.core.config import settings

print(f"App Name: {settings.APP_NAME}")
print(f"Debug: {settings.DEBUG}")
print(f"Database: {settings.DATABASE_URL}")
print(f"OpenAI Key: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Not Set'}")
```

### 方法 2: 命令行

```bash
python -c "from api.core.config import settings; print('✅ Config loaded')"
```

---

## 🐛 常见问题

### 问题 1: ValidationError: Extra inputs are not permitted

**原因**: `.env` 文件中的变量未在 `Settings` 类中定义

**解决**: 已修复 - 配置设置为 `extra="ignore"`，会自动忽略未定义的变量

### 问题 2: .env 文件不生效

**检查**:
1. 文件名是否正确（`.env` 不是 `env` 或 `.env.txt`）
2. 文件是否在项目根目录
3. 环境变量名称是否拼写正确

```bash
# 检查文件
ls -la .env

# 查看内容
cat .env
```

### 问题 3: 变量值包含特殊字符

使用引号包裹：

```bash
# 正确
DATABASE_PASSWORD="p@ssw0rd!#$"
SECRET_KEY="key-with-special-chars!@#"

# 错误
DATABASE_PASSWORD=p@ssw0rd!#$  # 特殊字符会导致解析错误
```

---

## 📚 相关文档

- [快速开始](./QUICK_START.md)
- [本地开发设置](./LOCAL_DEVCONTAINER_SETUP.md)
- [Python 版本指南](./PYTHON_VERSION_GUIDE.md)
- [API 使用指南](./API_USAGE_GUIDE.md)

---

## 💡 提示

1. **开发环境**: 可以使用简单的配置
2. **生产环境**: 必须使用强密码和安全配置
3. **团队协作**: 使用 `.env.example` 作为配置模板
4. **CI/CD**: 通过环境变量或密钥管理服务注入配置

---

**配置完成后，启动 API 测试是否生效！** 🚀

```bash
uvicorn api.main:app --reload
```
