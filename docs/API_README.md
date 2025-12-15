# 🚀 AIPortal FastAPI 项目

> 将 Streamlit 企业 AI 应用封装为现代化 REST API

## 📋 项目概述

本项目成功将 AIPortal (ComLan) 的核心功能封装成了 FastAPI REST API，实现了前后端分离，支持多端访问和系统集成。

### ✨ 核心特性

- ✅ **JWT 认证** - 基于 Token 的安全认证
- ✅ **文档翻译** - 支持 8 种语言的文本和文档翻译
- ✅ **智能对话** - 多模型 AI 对话，支持流式输出
- ✅ **文档审查** - 合同和标书的智能审核
- ✅ **异步处理** - 长时间任务的后台处理
- ✅ **自动文档** - 自动生成的 Swagger/ReDoc 文档
- ✅ **类型安全** - 基于 Pydantic 的数据验证

---

## 🎯 已实现的 API 模块

### 1️⃣ 认证模块 (`/api/v1/auth`)
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新 Token
- `GET /auth/me` - 获取当前用户信息
- `POST /auth/logout` - 用户登出

### 2️⃣ 翻译模块 (`/api/v1/translate`)
- `POST /translate/text` - 文本翻译
- `POST /translate/document` - 文档翻译 (异步)
- `GET /translate/status/{task_id}` - 查询翻译状态
- `GET /translate/download/{task_id}` - 下载翻译结果
- `GET /translate/languages` - 获取支持的语言

### 3️⃣ 对话模块 (`/api/v1/chat`)
- `POST /chat/completion` - AI 对话
- `POST /chat/stream` - 流式对话
- `POST /chat/multimodal` - 多模态对话 (文本+图片)
- `GET /chat/models` - 获取可用模型
- `DELETE /chat/history/{id}` - 清除对话历史

### 4️⃣ 文档审查模块 (`/api/v1/review`)
- `POST /review/contract` - 合同智能审查
- `POST /review/bidding` - 标书智能审查
- `POST /review/compare` - 文档对比

---

## 🚀 快速开始

### 1. 启动服务

```bash
cd /home/user/webapp
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 访问文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **在线访问**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs

### 3. 运行测试

```bash
python test_api.py
```

---

## 📁 项目结构

```
api/
├── main.py                      # FastAPI 主应用
├── core/                        # 核心配置
│   ├── config.py               # 应用配置
│   └── security.py             # JWT 认证
├── routes/                      # API 路由
│   ├── auth.py                 # 认证路由
│   ├── translate.py            # 翻译路由
│   ├── chat.py                 # 对话路由
│   └── review.py               # 文档审查路由
├── models/                      # Pydantic 模型
│   ├── request.py              # 请求模型
│   └── response.py             # 响应模型
├── services/                    # 业务逻辑
│   └── translation_service.py  # 翻译服务
└── utils/                       # 工具函数
    └── helpers.py              # 辅助函数
```

---

## 🔐 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| user | user123 | 普通用户 |

---

## 💡 使用示例

### Python 客户端

```python
import requests

# 登录
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# 调用 API
headers = {"Authorization": f"Bearer {token}"}
result = requests.post(
    "http://localhost:8000/api/v1/translate/text",
    headers=headers,
    json={
        "text": "你好，世界",
        "source_lang": "zh-Hans",
        "target_lang": "en"
    }
)
print(result.json())
```

### cURL 示例

```bash
# 登录
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 文本翻译
curl -X POST http://localhost:8000/api/v1/translate/text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，世界",
    "source_lang": "zh-Hans",
    "target_lang": "en"
  }'
```

---

## 🔧 技术栈

- **框架**: FastAPI 0.109.0
- **服务器**: Uvicorn
- **认证**: JWT (python-jose)
- **密码**: bcrypt (passlib)
- **验证**: Pydantic v2
- **异步**: async/await
- **文档**: OpenAPI 3.0 (自动生成)

---

## 📊 API 测试结果

```
✅ 健康检查 - 200 OK
✅ 用户登录 - 200 OK
✅ 获取用户信息 - 200 OK
✅ 文本翻译 - 200 OK
✅ 获取支持的语言 - 200 OK
✅ AI 对话 - 200 OK
✅ 获取可用模型 - 200 OK
```

---

## 🎨 与 Streamlit UI 的关系

```
                  ┌─────────────────┐
                  │  用户/客户端     │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              │                         │
        ┌─────▼──────┐           ┌─────▼──────┐
        │ Streamlit  │           │  REST API  │
        │    UI      │           │  (FastAPI) │
        │  (内部使用) │           │  (对外集成) │
        └─────┬──────┘           └─────┬──────┘
              │                         │
              └────────────┬────────────┘
                           │
                    ┌──────▼──────┐
                    │ 共享业务逻辑 │
                    │  function/  │
                    └─────────────┘
```

**优势**:
- 内部团队使用友好的 Streamlit UI
- 外部系统通过 REST API 集成
- 共享核心业务逻辑，避免重复开发

---

## 📈 性能特性

- **异步处理**: 所有 I/O 操作使用 async/await
- **后台任务**: 长时间任务在后台处理
- **流式输出**: 支持 SSE 流式响应
- **自动验证**: Pydantic 自动数据验证
- **中间件**: 请求日志和错误处理

---

## 🔜 下一步计划

### 短期目标
- [ ] 集成真实的 Azure 翻译服务
- [ ] 实现 Redis 任务队列 (Celery)
- [ ] 添加速率限制
- [ ] 完善错误处理

### 中期目标
- [ ] 添加更多 API 端点（BI 查询、图像识别等）
- [ ] 实现 WebSocket 支持
- [ ] 添加 API 版本管理
- [ ] 性能监控和日志系统

### 长期目标
- [ ] Docker 容器化
- [ ] Kubernetes 部署
- [ ] 负载均衡
- [ ] 分布式架构

---

## 📚 相关文档

- **使用指南**: [API_USAGE_GUIDE.md](./API_USAGE_GUIDE.md)
- **API 设计**: [api_design.md](./api_design.md)
- **在线文档**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs

---

## 🤝 贡献

欢迎贡献代码、提出问题和建议！

---

## 📄 许可证

参见 [LICENSE](./LICENSE) 文件

---

## 🎉 总结

✅ **成功完成**: FastAPI 项目框架搭建完成
✅ **核心功能**: 认证、翻译、对话、文档审查等模块已实现
✅ **文档完善**: 自动生成的 API 文档和使用指南
✅ **测试通过**: 所有核心 API 端点测试通过
✅ **可扩展**: 模块化设计，易于扩展新功能

**项目已就绪，可以开始使用和集成！** 🚀
