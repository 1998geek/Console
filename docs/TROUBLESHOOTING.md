# 🔧 故障排查指南

本文档包含常见问题和解决方案。

---

## 🐍 Python 版本问题

### 问题: Python 3.13 安装 Pydantic 失败

**错误信息**:
```
Building wheel for pydantic-core (pyproject.toml) ... error
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

**原因**: 
- Python 3.13 是新版本，一些旧版本的包不兼容
- `pydantic==2.5.3` 的依赖 `pydantic-core` 不支持 Python 3.13

**解决方案 1: 升级 Pydantic（推荐）**

已经在 `requirements_api.txt` 中更新：

```bash
# 重新安装
pip install -r requirements_api.txt
```

新版本要求：
- `pydantic>=2.8.2` - 支持 Python 3.13
- `pydantic-settings>=2.3.0` - 支持 Python 3.13

**解决方案 2: 使用 Python 3.12**

如果升级 Pydantic 有其他兼容性问题，使用 Python 3.12：

```bash
# 使用 pyenv
pyenv install 3.12.7
pyenv local 3.12.7

# 或使用 conda
conda create -n aiportal python=3.12
conda activate aiportal

# 重新安装依赖
pip install -r requirements_api.txt
```

**解决方案 3: 使用预编译的 wheel**

```bash
# 先升级 pip
pip install --upgrade pip

# 尝试从不同源安装
pip install --no-cache-dir pydantic>=2.8.2
pip install -r requirements_api.txt
```

---

## 📦 依赖安装问题

### 问题: pip 安装超时

**解决方案**: 使用国内镜像

```bash
# 临时使用清华镜像
pip install -r requirements_api.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements_api.txt -i https://mirrors.aliyun.com/pypi/simple/

# 永久配置（推荐）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题: 编译错误（gcc、rust 等）

**错误信息**:
```
error: command 'gcc' failed
unable to execute 'cargo': No such file or directory
```

**解决方案**: 安装编译工具

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential python3-dev libssl-dev libffi-dev

# macOS
xcode-select --install
brew install rust

# Windows
# 安装 Visual Studio Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### 问题: psycopg2-binary 安装失败

**解决方案**:

```bash
# 安装 PostgreSQL 开发库
# Ubuntu/Debian
sudo apt-get install libpq-dev

# macOS
brew install postgresql

# 或使用 psycopg2-binary 替代
pip install psycopg2-binary
```

---

## 🐳 Docker / Dev Container 问题

### 问题: Dev Container 构建失败

**解决方案 1**: 清理 Docker 缓存

```bash
# 清理所有未使用的资源
docker system prune -a

# 在 VS Code 中重新构建
# Ctrl+Shift+P → Dev Containers: Rebuild Container Without Cache
```

**解决方案 2**: 检查 Dockerfile

确保 Dockerfile 使用兼容的 Python 版本：

```dockerfile
# 使用 Python 3.12 而不是 3.13
FROM python:3.12-slim

# 或指定确切版本
FROM python:3.12.7-slim
```

**解决方案 3**: 手动构建测试

```bash
cd .devcontainer
docker build -t aiportal-test .
docker run -it aiportal-test /bin/bash
# 在容器内测试安装
pip install -r /app/requirements_api.txt
```

### 问题: 容器启动后依赖未安装

**检查 postCreateCommand**:

查看 `.devcontainer/devcontainer.json`:

```json
{
  "postCreateCommand": "pip install -r requirements_api.txt && echo '✅ Dependencies installed'"
}
```

**手动安装**:

```bash
# 在容器内手动执行
pip install -r requirements_api.txt
```

---

## 🌐 网络和端口问题

### 问题: 端口 8000 被占用

**错误信息**:
```
ERROR: [Errno 48] Address already in use
```

**解决方案**:

```bash
# Linux/macOS - 查找占用端口的进程
lsof -i :8000
# 或
netstat -ano | grep 8000

# 杀死进程
kill -9 <PID>

# Windows PowerShell
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 或使用其他端口
uvicorn api.main:app --port 8001
```

### 问题: 无法访问 localhost:8000

**可能原因**:
1. 服务未启动
2. 防火墙阻止
3. 绑定地址问题

**解决方案**:

```bash
# 1. 确认服务正在运行
ps aux | grep uvicorn

# 2. 检查端口监听
netstat -ano | grep 8000

# 3. 使用 0.0.0.0 绑定所有接口
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 4. 检查防火墙
# Linux
sudo ufw status
sudo ufw allow 8000

# macOS
# 系统偏好设置 → 安全性与隐私 → 防火墙
```

---

## 📝 模块导入问题

### 问题: ModuleNotFoundError: No module named 'api'

**解决方案 1**: 设置 PYTHONPATH

```bash
# 临时设置
export PYTHONPATH=/path/to/AI_Portal:$PYTHONPATH

# 或
export PYTHONPATH=$(pwd):$PYTHONPATH

# 验证
echo $PYTHONPATH
```

**解决方案 2**: 使用正确的工作目录

```bash
# 确保在项目根目录
cd /path/to/AI_Portal

# 验证
pwd  # 应该显示 AI_Portal 目录

# 启动服务
python -m uvicorn api.main:app --reload
```

**解决方案 3**: 在 VS Code 中设置

创建或更新 `.vscode/settings.json`:

```json
{
  "python.analysis.extraPaths": [
    "${workspaceFolder}"
  ],
  "terminal.integrated.env.linux": {
    "PYTHONPATH": "${workspaceFolder}:${env:PYTHONPATH}"
  }
}
```

### 问题: ImportError: cannot import name 'xxx'

**解决方案**:

```bash
# 1. 检查文件是否存在
ls -la api/core/config.py

# 2. 检查 __init__.py
ls -la api/__init__.py
ls -la api/core/__init__.py

# 3. 清理 Python 缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 4. 重新安装
pip install --force-reinstall -r requirements_api.txt
```

---

## 🔐 认证问题

### 问题: 401 Unauthorized

**可能原因**:
1. Token 过期
2. Token 格式错误
3. 未提供 Token

**解决方案**:

```bash
# 1. 重新登录获取新 Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. 检查 Token 格式
# 正确格式: Authorization: Bearer <token>
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGc..."

# 3. 在 Swagger UI 中测试
# 访问 /docs，点击右上角 Authorize 按钮
```

### 问题: 403 Forbidden

**原因**: 权限不足（需要管理员权限）

**解决方案**: 使用管理员账号登录

```bash
# 使用 admin 账号
username: admin
password: admin123
```

---

## 📄 文件上传问题

### 问题: File too large

**错误**: `File size exceeds maximum allowed size`

**解决方案**: 修改 `api/core/config.py`:

```python
# Upload Settings
MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 改为 100MB
```

### 问题: File type not allowed

**错误**: `File type .xyz not allowed`

**解决方案**: 添加允许的文件类型

```python
# api/core/config.py
ALLOWED_EXTENSIONS: set = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".txt",
    ".xyz"  # 添加新类型
}
```

---

## 🔍 调试技巧

### 启用详细日志

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 或在启动时指定
uvicorn api.main:app --reload --log-level debug
```

### 使用 VS Code 调试器

1. 按 `F5` 启动调试
2. 在代码中设置断点
3. 查看变量值
4. 逐步执行

### 查看详细错误

在 `api/core/config.py` 中：

```python
DEBUG: bool = True  # 开启调试模式
```

在 FastAPI 中会显示完整的错误堆栈。

---

## 🆘 仍然无法解决？

### 收集信息

```bash
# 1. Python 版本
python --version

# 2. 系统信息
uname -a  # Linux/macOS
systeminfo  # Windows

# 3. 已安装的包
pip list

# 4. 详细错误日志
pip install -r requirements_api.txt 2>&1 | tee install.log
```

### 提交 Issue

访问: https://github.com/ComlanOfficial/AI_Portal/issues

包含以下信息：
- Python 版本
- 操作系统
- 完整错误日志
- 已尝试的解决方案

---

## 💡 预防建议

### 1. 使用虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements_api.txt
```

### 2. 固定依赖版本

在生产环境使用精确版本：

```bash
# 生成精确版本的 requirements.txt
pip freeze > requirements-lock.txt

# 使用固定版本安装
pip install -r requirements-lock.txt
```

### 3. 定期更新

```bash
# 检查过期的包
pip list --outdated

# 更新单个包
pip install --upgrade pydantic

# 测试后更新 requirements_api.txt
```

### 4. 使用 Docker

最稳定的方式是使用 Docker 容器：

```bash
docker-compose -f docker-compose.api.yml up
```

---

## 📚 相关资源

- [FastAPI 文档](https://fastapi.tiangolo.com)
- [Pydantic 文档](https://docs.pydantic.dev)
- [Python 官方文档](https://docs.python.org)
- [Docker 文档](https://docs.docker.com)

---

**最后更新**: 2024-11-20
