# 🚀 本地 Dev Container 运行 FastAPI 指南

## 📋 前提条件

确保你已经安装了：
- ✅ [Visual Studio Code](https://code.visualstudio.com/)
- ✅ [Docker Desktop](https://www.docker.com/products/docker-desktop)
- ✅ VS Code 扩展: [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

## 📥 步骤 1: 拉取最新代码

```bash
# 进入项目目录
cd /path/to/AI_Portal

# 拉取最新代码
git fetch origin

# 查看分支
git branch -a

# 切换到 FastAPI 分支
git checkout feature/fastapi-implementation

# 或者拉取 main 分支（如果 PR 已合并）
git checkout main
git pull origin main
```

---

## 🐳 步骤 2: 打开 Dev Container

### 方法 1: 通过 VS Code 命令面板

1. 打开 VS Code
2. 打开项目文件夹: `File` → `Open Folder` → 选择 `AI_Portal`
3. 按 `F1` 或 `Ctrl+Shift+P` (Mac: `Cmd+Shift+P`)
4. 输入: `Dev Containers: Reopen in Container`
5. 等待容器构建（首次需要几分钟）

### 方法 2: 通过右下角提示

1. 打开项目后，右下角会提示: "Reopen in Container"
2. 点击 "Reopen in Container"
3. 等待构建完成

### 方法 3: 通过 Docker Compose（手动）

```bash
# 进入项目目录
cd AI_Portal

# 构建并启动容器
docker-compose -f .devcontainer/docker-compose.yml up -d

# 进入容器
docker exec -it ai-portal-dev bash
```

---

## 📦 步骤 3: 安装 FastAPI 依赖

容器启动后，在 VS Code 终端中执行：

```bash
# 确认当前目录
pwd
# 应该显示: /app 或项目根目录

# 安装 FastAPI 依赖
pip install -r requirements_api.txt

# 验证安装
python -c "import fastapi; print(fastapi.__version__)"
```

---

## 🔧 步骤 4: 配置环境变量（可选）

### 创建 `.env` 文件

```bash
# 在项目根目录创建 .env 文件
cat > .env << 'EOF'
# Application
DEBUG=true

# Security (生产环境必须改！)
SECRET_KEY=your-super-secret-key-change-me-in-production

# Database (如果需要)
# DATABASE_URL=postgresql://user:password@localhost:5432/aiportal

# Azure Services (如果需要)
# AZURE_STORAGE_CONNECTION_STRING=your-connection-string
# AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
# AZURE_OPENAI_KEY=your-api-key

# OpenAI (如果需要)
# OPENAI_API_KEY=sk-your-openai-key

# CORS (开发环境允许所有)
CORS_ORIGINS=["*"]
EOF
```

**注意**: `.env` 文件不会提交到 Git（已在 `.gitignore` 中）

---

## 🚀 步骤 5: 启动 FastAPI 服务

### 方法 1: 使用 Uvicorn 命令

```bash
# 开发模式（自动重载）
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 或者简写
uvicorn api.main:app --reload
```

### 方法 2: 直接运行 Python

```bash
python -m api.main
```

### 方法 3: 使用 VS Code 调试

创建 `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI: Run API",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

然后按 `F5` 启动调试。

---

## 🌐 步骤 6: 访问 API

### 本地访问地址

服务启动后，在浏览器访问：

| 服务 | URL | 说明 |
|------|-----|------|
| **API 根路径** | http://localhost:8000 | 查看 API 信息 |
| **健康检查** | http://localhost:8000/health | 检查服务状态 |
| **Swagger UI** | http://localhost:8000/docs | 交互式 API 文档 ⭐ |
| **ReDoc** | http://localhost:8000/redoc | 另一种文档格式 |
| **OpenAPI JSON** | http://localhost:8000/openapi.json | API 规范 |

### 推荐：先访问 Swagger UI

打开 http://localhost:8000/docs 你会看到：

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-01-swagger-ui-simple.png)

在这里可以：
- 📖 查看所有 API 端点
- 🧪 直接测试 API
- 🔐 输入 Token 认证
- 📝 查看请求/响应示例

---

## 🧪 步骤 7: 测试 API

### 测试 1: 健康检查（无需认证）

```bash
curl http://localhost:8000/health
```

**预期输出**:
```json
{
  "status": "healthy",
  "timestamp": 1700000000.123
}
```

### 测试 2: 登录获取 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**预期输出**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**保存 Token**:
```bash
# Linux/Mac
export TOKEN="your_access_token_here"

# Windows PowerShell
$TOKEN="your_access_token_here"
```

### 测试 3: 使用 Token 调用 API

```bash
curl -X POST http://localhost:8000/api/v1/translate/text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，世界",
    "source_lang": "zh-Hans",
    "target_lang": "en",
    "use_cloud": true
  }'
```

### 测试 4: 运行完整测试脚本

```bash
# 在 Dev Container 中运行
python test_api.py
```

**预期输出**:
```
🚀🚀🚀 AIPortal FastAPI 功能测试 🚀🚀🚀
============================================================
  1. 健康检查
============================================================
状态码: 200
✅ Health check passed

============================================================
  2. 用户登录
============================================================
状态码: 200
✅ 登录成功!

... (更多测试)

✅ 所有测试完成!
```

---

## 🔥 步骤 8: 同时运行 Streamlit UI（可选）

如果你想同时运行 Streamlit UI 和 FastAPI：

### 终端 1: 运行 FastAPI

```bash
uvicorn api.main:app --reload --port 8000
```

### 终端 2: 运行 Streamlit

```bash
streamlit run streamlit_app.py --server.port 8501
```

### 访问

- **FastAPI**: http://localhost:8000/docs
- **Streamlit**: http://localhost:8501

---

## 🐛 常见问题排查

### 问题 1: 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 查看占用 8000 端口的进程
lsof -i :8000

# 或者
netstat -ano | grep 8000

# 杀死进程
kill -9 <PID>

# 或者使用其他端口
uvicorn api.main:app --port 8001
```

### 问题 2: 模块未找到

**错误**: `ModuleNotFoundError: No module named 'fastapi'`

**解决**:
```bash
# 确保安装了依赖
pip install -r requirements_api.txt

# 检查 Python 路径
which python
python --version

# 如果有多个 Python，使用 python3
python3 -m pip install -r requirements_api.txt
python3 -m uvicorn api.main:app --reload
```

### 问题 3: 导入错误

**错误**: `ImportError: cannot import name 'xxx'`

**解决**:
```bash
# 确保在项目根目录
pwd  # 应该显示 /app 或项目根目录

# 设置 PYTHONPATH
export PYTHONPATH=/app:$PYTHONPATH

# 或者
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### 问题 4: Dev Container 无法启动

**解决**:
```bash
# 1. 清理 Docker
docker system prune -a

# 2. 重新构建容器
# 在 VS Code 中: Ctrl+Shift+P
# 输入: Dev Containers: Rebuild Container

# 3. 或者手动构建
cd .devcontainer
docker build -t aiportal-dev .
```

### 问题 5: 权限问题

**错误**: `Permission denied`

**解决**:
```bash
# 修改文件权限
chmod -R 755 api/
chmod +x api/main.py

# 或者以 root 运行
sudo uvicorn api.main:app --reload
```

---

## 📝 VS Code 任务配置

创建 `.vscode/tasks.json` 快速启动：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start FastAPI",
      "type": "shell",
      "command": "uvicorn api.main:app --reload --host 0.0.0.0 --port 8000",
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Start Streamlit",
      "type": "shell",
      "command": "streamlit run streamlit_app.py --server.port 8501",
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Run API Tests",
      "type": "shell",
      "command": "python test_api.py",
      "problemMatcher": []
    },
    {
      "label": "Start All Services",
      "dependsOn": ["Start FastAPI", "Start Streamlit"],
      "problemMatcher": []
    }
  ]
}
```

使用方法：
1. 按 `Ctrl+Shift+P`
2. 输入 `Tasks: Run Task`
3. 选择任务（如 "Start FastAPI"）

---

## 🎯 快速启动脚本

创建 `start_dev.sh`:

```bash
#!/bin/bash

echo "🚀 Starting AIPortal Development Environment"

# 检查是否在 Dev Container 中
if [ ! -f /.dockerenv ]; then
    echo "⚠️  Not in Dev Container. Please reopen in container first."
    exit 1
fi

# 安装依赖
echo "📦 Installing dependencies..."
pip install -r requirements_api.txt -q

# 启动 FastAPI
echo "🔥 Starting FastAPI on http://localhost:8000"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

使用：
```bash
chmod +x start_dev.sh
./start_dev.sh
```

---

## 📚 开发工作流

### 典型的开发流程：

```bash
# 1. 打开项目
code /path/to/AI_Portal

# 2. 在容器中重新打开 (F1 → Reopen in Container)

# 3. 安装依赖
pip install -r requirements_api.txt

# 4. 启动服务
uvicorn api.main:app --reload

# 5. 在浏览器访问
open http://localhost:8000/docs

# 6. 修改代码（会自动重载）

# 7. 测试
python test_api.py

# 8. 提交代码
git add .
git commit -m "feat: add new feature"
git push
```

---

## 🔗 相关链接

- **API 文档**: http://localhost:8000/docs
- **项目 README**: [API_README.md](./API_README.md)
- **使用指南**: [API_USAGE_GUIDE.md](./API_USAGE_GUIDE.md)
- **快速开始**: [QUICK_START.md](./QUICK_START.md)

---

## 💡 提示

### 开发时的最佳实践：

1. **使用 `--reload` 模式** - 代码修改自动重启
2. **查看日志** - 终端会显示所有请求日志
3. **使用 Swagger UI** - 测试 API 最方便
4. **环境变量** - 敏感信息放在 `.env` 文件
5. **代码格式化** - 使用 `black` 和 `isort`

```bash
# 安装开发工具
pip install black isort flake8

# 格式化代码
black api/
isort api/

# 检查代码质量
flake8 api/
```

---

## 🎉 开始开发吧！

现在你已经准备好在本地 Dev Container 中开发 FastAPI 了！

有任何问题，参考：
- 📖 [FastAPI 文档](https://fastapi.tiangolo.com)
- 📖 [Pydantic 文档](https://docs.pydantic.dev)
- 📖 [Uvicorn 文档](https://www.uvicorn.org)

Happy Coding! 🚀
