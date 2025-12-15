# 🎯 开发快速参考

## 🚀 快速启动

```bash
# 方法 1: 使用启动脚本（推荐）
./start_dev.sh

# 方法 2: 直接启动
uvicorn api.main:app --reload

# 方法 3: 使用 VS Code 调试
# 按 F5 选择 "FastAPI: Debug API"
```

## 🌐 访问地址

| 服务 | URL | 快捷键 |
|------|-----|--------|
| API 文档 | http://localhost:8000/docs | `Ctrl+Click` |
| ReDoc | http://localhost:8000/redoc | `Ctrl+Click` |
| API 根 | http://localhost:8000 | - |
| 健康检查 | http://localhost:8000/health | - |

## 🔐 测试账号

```
管理员: admin / admin123
用户:   user / user123
```

## 📋 常用命令

### 安装依赖
```bash
pip install -r requirements_api.txt
```

### 运行测试
```bash
python test_api.py
```

### 代码格式化
```bash
black api/
isort api/
```

### 查看日志
```bash
# API 日志会在终端实时显示
# 格式: METHOD /path - STATUS_CODE - TIME
```

## 🧪 快速测试

### 1. 登录获取 Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 2. 使用 Token
```bash
TOKEN="your_token_here"
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 3. 文本翻译
```bash
curl -X POST http://localhost:8000/api/v1/translate/text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好",
    "source_lang": "zh-Hans",
    "target_lang": "en"
  }'
```

## 🔧 VS Code 快捷操作

### 任务（Ctrl+Shift+P → Tasks: Run Task）
- `FastAPI: Start API Server` - 启动 API
- `Streamlit: Start UI` - 启动 UI
- `Test: Run API Tests` - 运行测试
- `Start All: API + UI` - 同时启动

### 调试（F5）
- `FastAPI: Debug API` - 调试 API
- `Streamlit: Debug UI` - 调试 UI
- `Python: Run Test Script` - 运行测试

### REST Client
打开 `api_test.http` 文件，点击 `Send Request` 测试 API

## 📁 项目结构

```
api/
├── main.py              # FastAPI 入口
├── core/                # 核心配置
│   ├── config.py       # 配置管理
│   └── security.py     # JWT 认证
├── routes/              # API 路由
│   ├── auth.py         # 认证
│   ├── translate.py    # 翻译
│   ├── chat.py         # 对话
│   └── review.py       # 文档审查
├── models/              # 数据模型
│   ├── request.py      # 请求模型
│   └── response.py     # 响应模型
├── services/            # 业务逻辑
│   └── translation_service.py
└── utils/               # 工具函数
    └── helpers.py
```

## 🐛 常见问题

### 端口被占用
```bash
# 查找进程
lsof -i :8000
# 杀死进程
kill -9 <PID>
```

### 模块未找到
```bash
# 安装依赖
pip install -r requirements_api.txt
# 设置 PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### 权限问题
```bash
chmod +x start_dev.sh
chmod -R 755 api/
```

## 💡 开发提示

1. **自动重载**: 修改代码后自动重启（使用 `--reload`）
2. **查看日志**: 所有请求会在终端显示
3. **Swagger UI**: 最方便的测试方式
4. **REST Client**: VS Code 扩展测试 API
5. **环境变量**: 敏感信息放 `.env` 文件

## 📚 文档链接

- [完整文档](./LOCAL_DEVCONTAINER_SETUP.md)
- [API 使用指南](./API_USAGE_GUIDE.md)
- [快速开始](./QUICK_START.md)
- [项目说明](./API_README.md)

## 🎯 工作流程

```
1. 修改代码 → 2. 自动重载 → 3. 测试 API → 4. 提交代码
```

---

**Happy Coding! 🚀**
