# 📦 安装指南

## 🐍 Python 版本要求

### 推荐版本
- **Python 3.12.x** ⭐ (推荐，最稳定)
- **Python 3.11.x** (完全支持)
- **Python 3.13.x** (需要更新的 Pydantic 版本)

### ⚠️ 注意事项

**Python 3.13** 是新版本，部分依赖包可能不兼容。我们已经更新了 `requirements_api.txt` 来支持它，但如果遇到问题，请使用 Python 3.12。

---

## 🚀 快速安装（3 种方法）

### 方法 1: 本地直接安装（最简单）

```bash
# 1. 克隆仓库
git clone https://github.com/ComlanOfficial/AI_Portal.git
cd AI_Portal

# 2. 检查 Python 版本
python --version
# 如果是 3.13，建议切换到 3.12

# 3. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装依赖
pip install -r requirements_api.txt

# 6. 启动服务
./start_dev.sh
# 或
uvicorn api.main:app --reload

# 7. 访问
open http://localhost:8000/docs
```

### 方法 2: Dev Container（推荐开发者）

```bash
# 1. 确保已安装
- Visual Studio Code
- Docker Desktop
- Dev Containers 扩展

# 2. 克隆并打开项目
git clone https://github.com/ComlanOfficial/AI_Portal.git
cd AI_Portal
code .

# 3. 在容器中重新打开
# 按 F1 → "Dev Containers: Reopen in Container"

# 4. 等待容器构建（首次 3-5 分钟）
# 依赖会自动安装！

# 5. 启动服务
./start_dev.sh

# 6. 访问
http://localhost:8000/docs
```

### 方法 3: Docker（生产环境）

```bash
# 1. 克隆仓库
git clone https://github.com/ComlanOfficial/AI_Portal.git
cd AI_Portal

# 2. 使用 Docker Compose
docker-compose -f docker-compose.api.yml up

# 3. 访问
http://localhost:8000/docs
```

---

## 🔧 安装步骤详解

### 步骤 1: 检查 Python 版本

```bash
python --version
```

**如果显示 Python 3.13**:

有两个选择：

**选择 A: 使用 Python 3.12（推荐）**

```bash
# 使用 pyenv
pyenv install 3.12.7
pyenv local 3.12.7

# 使用 conda
conda create -n aiportal python=3.12
conda activate aiportal

# 使用 apt (Ubuntu)
sudo apt install python3.12 python3.12-venv

# 使用 brew (macOS)
brew install python@3.12
```

**选择 B: 继续使用 Python 3.13**

我们已经更新了依赖，应该可以工作。如果遇到问题，查看 [故障排查](./docs/TROUBLESHOOTING.md)。

### 步骤 2: 创建虚拟环境

**为什么需要虚拟环境？**
- 隔离项目依赖
- 避免版本冲突
- 易于管理

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate

# Windows CMD
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# 验证（应该显示虚拟环境路径）
which python
# 或
where python
```

### 步骤 3: 升级 pip

```bash
# 升级到最新版本
pip install --upgrade pip

# 验证
pip --version
```

### 步骤 4: 安装依赖

**方式 A: 一次性安装**

```bash
pip install -r requirements_api.txt
```

**方式 B: 使用国内镜像（更快）**

```bash
# 清华镜像
pip install -r requirements_api.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements_api.txt
```

**方式 C: 分步安装（排查问题）**

```bash
# 1. 核心依赖
pip install fastapi uvicorn

# 2. Pydantic（确保版本正确）
pip install "pydantic>=2.8.2" "pydantic-settings>=2.3.0"

# 3. 其他依赖
pip install -r requirements_api.txt
```

### 步骤 5: 验证安装

```bash
# 检查关键包
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"

# 列出所有已安装的包
pip list
```

### 步骤 6: 启动服务

```bash
# 方法 1: 使用启动脚本
chmod +x start_dev.sh
./start_dev.sh

# 方法 2: 直接启动
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 方法 3: 使用 Python 模块
python -m uvicorn api.main:app --reload
```

**期望输出**:

```
🚀 Starting AIPortal API v1.0.0
📁 Upload directory: /tmp/uploads
🔐 Authentication: JWT with HS256
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 步骤 7: 测试访问

打开浏览器访问：

- http://localhost:8000 - API 根路径
- http://localhost:8000/docs - Swagger UI ⭐
- http://localhost:8000/redoc - ReDoc
- http://localhost:8000/health - 健康检查

---

## 🐛 常见安装问题

### 问题 1: pydantic-core 编译失败

**错误**: `Building wheel for pydantic-core ... error`

**解决**: 
1. 使用 Python 3.12
2. 或更新 Pydantic: `pip install "pydantic>=2.8.2"`

**详细**: 查看 [故障排查](./docs/TROUBLESHOOTING.md#python-版本问题)

### 问题 2: 缺少编译工具

**错误**: `error: command 'gcc' failed`

**解决**:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# macOS
xcode-select --install

# Windows
# 安装 Visual Studio Build Tools
```

### 问题 3: 网络超时

**错误**: `TimeoutError` 或 `ReadTimeout`

**解决**: 使用国内镜像
```bash
pip install -r requirements_api.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 4: 权限错误

**错误**: `Permission denied`

**解决**:
```bash
# 不要使用 sudo pip
# 使用虚拟环境或用户安装
pip install --user -r requirements_api.txt
```

---

## ✅ 安装验证清单

完成以下检查确保安装成功：

```bash
# ✓ Python 版本
python --version  # 应该是 3.11 或 3.12

# ✓ 虚拟环境激活
which python  # 应该显示 venv 路径

# ✓ 依赖已安装
pip list | grep fastapi
pip list | grep pydantic

# ✓ 服务可以启动
uvicorn api.main:app --reload &
sleep 3

# ✓ 健康检查通过
curl http://localhost:8000/health

# ✓ API 文档可访问
curl http://localhost:8000/openapi.json | head -10

# ✓ 停止服务
pkill uvicorn
```

**全部 ✓ 则安装成功！**

---

## 📚 下一步

安装完成后：

1. **阅读文档**: [docs/QUICK_START.md](./docs/QUICK_START.md)
2. **查看 API**: http://localhost:8000/docs
3. **运行测试**: `python test_api.py`
4. **开始开发**: [docs/DEV_QUICKREF.md](./docs/DEV_QUICKREF.md)

---

## 🆘 需要帮助？

- 📖 [故障排查指南](./docs/TROUBLESHOOTING.md)
- 📖 [完整文档](./docs/README.md)
- 🐛 [提交 Issue](https://github.com/ComlanOfficial/AI_Portal/issues)

---

**祝你安装顺利！** 🎉
