# 🐍 Python 版本兼容性指南

## ⚠️ Python 3.13 兼容性问题

如果你在安装依赖时遇到 `pydantic-core` 编译错误，这是因为使用了不兼容 Python 3.13 的旧版本。

---

## 🔍 问题表现

### 错误信息
```
Building wheel for pydantic-core (pyproject.toml) ... error
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
ERROR: Failed building wheel for pydantic-core
```

### 原因
- Python 3.13 更改了一些内部 API
- 旧版本的 Pydantic（< 2.9.0）与 Python 3.13 不兼容

---

## ✅ 解决方案

### 方案 1: 使用最新的 requirements_api.txt（推荐）

```bash
# 拉取最新代码
git pull origin feature/fastapi-implementation

# 重新安装依赖
pip install -r requirements_api.txt
```

**最新版本要求**:
- `pydantic>=2.9.0` - Python 3.13 兼容
- `pydantic-settings>=2.5.0` - Python 3.13 兼容

---

### 方案 2: 手动升级 Pydantic

```bash
# 先升级 pip
pip install --upgrade pip

# 安装最新版本的 Pydantic
pip install "pydantic>=2.9.0" "pydantic-settings>=2.5.0"

# 然后安装其他依赖
pip install -r requirements_api.txt
```

---

### 方案 3: 使用 Python 3.12（如果需要稳定版本）

如果你想使用更稳定的 Python 版本：

#### 使用 pyenv
```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 安装 Python 3.12
pyenv install 3.12.7

# 设置本地 Python 版本
pyenv local 3.12.7

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements_api.txt
```

#### 使用 conda
```bash
# 创建 Python 3.12 环境
conda create -n aiportal python=3.12

# 激活环境
conda activate aiportal

# 安装依赖
pip install -r requirements_api.txt
```

---

### 方案 4: 使用 Docker（最推荐）

使用 Dev Container 或 Docker 可以避免本地环境问题：

```bash
# 方法 A: 使用 Dev Container (VS Code)
# 1. 打开项目
# 2. F1 → "Dev Containers: Reopen in Container"
# 3. 容器会自动使用正确的 Python 版本

# 方法 B: 使用 Docker Compose
docker-compose -f docker-compose.api.yml up
```

---

## 📋 推荐的 Python 版本

| Python 版本 | 状态 | 推荐 | 说明 |
|------------|------|------|------|
| **3.12.x** | ✅ 稳定 | ⭐⭐⭐⭐⭐ | 最推荐，兼容性最好 |
| **3.13.x** | ✅ 支持 | ⭐⭐⭐⭐ | 需要 Pydantic ≥ 2.9.0 |
| **3.11.x** | ✅ 稳定 | ⭐⭐⭐⭐ | 完全兼容 |
| **3.10.x** | ✅ 稳定 | ⭐⭐⭐ | 可用，但建议升级 |
| **3.9.x**  | ⚠️ 老旧 | ⭐⭐ | 不推荐 |

---

## 🔧 完整安装步骤

### 步骤 1: 检查 Python 版本

```bash
python --version
# 或
python3 --version
```

### 步骤 2: 确保使用最新的 pip

```bash
pip install --upgrade pip
```

### 步骤 3: 安装依赖

```bash
# 方法 A: 直接安装
pip install -r requirements_api.txt

# 方法 B: 如果遇到问题，先升级关键依赖
pip install --upgrade "pydantic>=2.9.0" "pydantic-settings>=2.5.0"
pip install -r requirements_api.txt

# 方法 C: 使用虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements_api.txt
```

### 步骤 4: 验证安装

```bash
# 检查 Pydantic 版本
python -c "import pydantic; print(pydantic.__version__)"
# 应该显示 >= 2.9.0

# 检查 FastAPI 是否正常
python -c "import fastapi; print(fastapi.__version__)"

# 尝试启动服务
python -m uvicorn api.main:app --reload
```

---

## 🐛 其他常见问题

### 问题 1: `rust` 编译器相关错误

如果看到 Rust 相关的错误，说明系统缺少编译工具：

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y build-essential python3-dev
```

#### macOS
```bash
xcode-select --install
```

#### Windows
安装 [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

---

### 问题 2: 权限错误

```bash
# 如果遇到权限问题，使用 --user
pip install --user -r requirements_api.txt

# 或使用虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_api.txt
```

---

### 问题 3: 网络问题（中国大陆）

```bash
# 使用清华镜像
pip install -r requirements_api.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements_api.txt -i https://mirrors.aliyun.com/pypi/simple/
```

---

## 📦 完整的依赖版本要求

### 核心依赖
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.9.0           # Python 3.13 compatible
pydantic-settings>=2.5.0  # Python 3.13 compatible
```

### 安全相关
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

### 文件处理
```
aiofiles==23.2.1
httpx==0.26.0
python-dotenv
```

---

## 🎯 最佳实践

### 1. 使用虚拟环境

**为什么？**
- 隔离项目依赖
- 避免版本冲突
- 易于管理

**如何创建？**
```bash
# 创建虚拟环境
python -m venv .venv

# 激活（Linux/Mac）
source .venv/bin/activate

# 激活（Windows）
.venv\Scripts\activate

# 安装依赖
pip install -r requirements_api.txt

# 退出
deactivate
```

### 2. 使用 Dev Container（最推荐）

**优势**:
- ✅ 环境一致性
- ✅ 自动配置
- ✅ 避免本地问题
- ✅ 团队协作方便

**使用方法**:
1. 安装 Docker Desktop
2. 安装 VS Code + Dev Containers 扩展
3. 打开项目
4. F1 → "Dev Containers: Reopen in Container"

### 3. 固定依赖版本（生产环境）

在生产环境，建议使用固定版本：

```bash
# 生成精确版本列表
pip freeze > requirements-lock.txt

# 使用精确版本安装
pip install -r requirements-lock.txt
```

---

## 🆘 仍然遇到问题？

### 调试步骤

1. **清理 pip 缓存**
   ```bash
   pip cache purge
   ```

2. **重新安装 pip**
   ```bash
   python -m ensurepip --upgrade
   pip install --upgrade pip setuptools wheel
   ```

3. **检查 Python 环境**
   ```bash
   which python
   python --version
   pip --version
   ```

4. **使用 verbose 模式查看详细错误**
   ```bash
   pip install -r requirements_api.txt -v
   ```

5. **创建全新的虚拟环境**
   ```bash
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements_api.txt
   ```

---

## 📞 获取帮助

如果以上方法都无法解决问题，请：

1. 在 GitHub 提 Issue，包含：
   - Python 版本 (`python --version`)
   - 操作系统
   - 完整错误信息
   - 已尝试的解决方案

2. 查看相关文档：
   - [FastAPI 文档](https://fastapi.tiangolo.com/)
   - [Pydantic 文档](https://docs.pydantic.dev/)
   - [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)

---

## ✅ 验证安装成功

```bash
# 1. 检查所有依赖
pip list

# 2. 运行测试脚本
python test_api.py

# 3. 启动服务
uvicorn api.main:app --reload

# 4. 访问文档
curl http://localhost:8000/docs
# 或在浏览器打开 http://localhost:8000/docs
```

---

**祝你安装顺利！** 🚀

如有问题，参考上述步骤或在 GitHub 提 Issue。
