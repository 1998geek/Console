# 🚀 FastAPI 快速启动指南

## ⚡ 5 分钟快速上手

### 1️⃣ 启动服务

```bash
cd /home/user/webapp
python -m uvicorn api.main:app --reload
```

### 2️⃣ 访问文档

🌐 **在线访问**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs

或本地访问: http://localhost:8000/docs

### 3️⃣ 获取 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 4️⃣ 调用 API

```bash
# 保存 token
TOKEN="your_token_here"

# 文本翻译
curl -X POST http://localhost:8000/api/v1/translate/text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好",
    "source_lang": "zh-Hans",
    "target_lang": "en"
  }'
```

---

## 📦 核心端点

| 功能 | 方法 | 端点 | 需要认证 |
|------|------|------|---------|
| 登录 | POST | `/api/v1/auth/login` | ❌ |
| 文本翻译 | POST | `/api/v1/translate/text` | ✅ |
| 文档翻译 | POST | `/api/v1/translate/document` | ✅ |
| AI 对话 | POST | `/api/v1/chat/completion` | ✅ |
| 合同审查 | POST | `/api/v1/review/contract` | ✅ |
| 标书审查 | POST | `/api/v1/review/bidding` | ✅ |

---

## 🔐 测试账号

```
管理员: admin / admin123
用户: user / user123
```

---

## 🧪 运行测试

```bash
python test_api.py
```

---

## 📚 完整文档

- **使用指南**: [API_USAGE_GUIDE.md](./API_USAGE_GUIDE.md)
- **项目说明**: [API_README.md](./API_README.md)
- **设计文档**: [api_design.md](./api_design.md)

---

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -f Dockerfile.api -t aiportal-api .

# 运行容器
docker run -p 8000:8000 aiportal-api

# 或使用 docker-compose
docker-compose -f docker-compose.api.yml up
```

---

## 🎯 当前运行状态

✅ **Streamlit UI**: https://8501-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai
✅ **FastAPI**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai
✅ **API 文档**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs

---

**Happy Coding! 🎉**
