# AIPortal FastAPI 使用指南

## 🎉 恭喜！你的 FastAPI 服务已成功启动

### 📍 访问地址

- **API 服务**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai
- **交互式文档 (Swagger)**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs
- **ReDoc 文档**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/redoc

### 🔐 测试账号

| 用户类型 | 用户名 | 密码 | 权限 |
|---------|--------|------|------|
| 管理员 | admin | admin123 | 完全访问 |
| 普通用户 | user | user123 | 基础访问 |

---

## 🚀 快速开始

### 1. 登录获取 Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**响应示例**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. 使用 Token 访问 API

在所有后续请求中，在 Header 中添加 Token：

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📚 API 功能模块

### 🔐 认证模块 (Authentication)

#### 登录
```bash
POST /api/v1/auth/login
```

#### 刷新 Token
```bash
POST /api/v1/auth/refresh
Body: {"refresh_token": "your_refresh_token"}
```

#### 获取当前用户信息
```bash
GET /api/v1/auth/me
Authorization: Bearer YOUR_TOKEN
```

#### 登出
```bash
POST /api/v1/auth/logout
Authorization: Bearer YOUR_TOKEN
```

---

### 🌐 文档翻译模块 (Translation)

#### 文本翻译
```bash
POST /api/v1/translate/text
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "text": "你好，世界",
  "source_lang": "zh-Hans",
  "target_lang": "en",
  "use_cloud": true
}
```

#### 文档翻译 (异步)
```bash
POST /api/v1/translate/document
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

file: (binary)
source_lang: zh-Hans
target_lang: en
use_cloud: true
```

**响应**: 返回 `task_id`

#### 查询翻译状态
```bash
GET /api/v1/translate/status/{task_id}
Authorization: Bearer YOUR_TOKEN
```

#### 下载翻译结果
```bash
GET /api/v1/translate/download/{task_id}
Authorization: Bearer YOUR_TOKEN
```

#### 获取支持的语言
```bash
GET /api/v1/translate/languages
```

**支持的语言**:
- `zh-Hans` - 简体中文
- `zh-Hant` - 繁体中文
- `en` - 英语
- `ja` - 日语
- `ko` - 韩语
- `fr` - 法语
- `de` - 德语
- `es` - 西班牙语

---

### 💬 智能对话模块 (Chat)

#### 普通对话
```bash
POST /api/v1/chat/completion
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "message": "请帮我写一段 Python 代码",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2000,
  "history": []
}
```

#### 流式对话
```bash
POST /api/v1/chat/stream
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "message": "讲一个故事",
  "model": "gpt-4"
}
```

#### 多模态对话 (图文)
```bash
POST /api/v1/chat/multimodal
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "message": "这张图片是什么？",
  "image_urls": ["https://example.com/image.jpg"],
  "model": "gpt-4-vision"
}
```

#### 获取可用模型
```bash
GET /api/v1/chat/models
```

---

### 📄 文档审查模块 (Document Review)

#### 合同智能审查
```bash
POST /api/v1/review/contract
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

file: (binary contract file)
analysis_type: comprehensive
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "overall_score": 72.5,
    "risk_level": "medium",
    "risks": [...],
    "suggestions": [...],
    "summary": "..."
  }
}
```

#### 标书智能审查
```bash
POST /api/v1/review/bidding
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

file: (binary bidding document)
check_compliance: true
check_completeness: true
```

#### 文档对比
```bash
POST /api/v1/review/compare
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

file1: (binary)
file2: (binary)
compare_mode: detailed
```

---

## 🔧 Python 客户端示例

```python
import requests

# 1. 登录
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = login_response.json()["access_token"]

# 2. 设置 Header
headers = {"Authorization": f"Bearer {token}"}

# 3. 文本翻译
translate_response = requests.post(
    "http://localhost:8000/api/v1/translate/text",
    headers=headers,
    json={
        "text": "你好，世界",
        "source_lang": "zh-Hans",
        "target_lang": "en",
        "use_cloud": True
    }
)
print(translate_response.json())

# 4. 对话
chat_response = requests.post(
    "http://localhost:8000/api/v1/chat/completion",
    headers=headers,
    json={
        "message": "写一首诗",
        "model": "gpt-4"
    }
)
print(chat_response.json())

# 5. 文件上传 - 合同审查
with open("contract.pdf", "rb") as f:
    review_response = requests.post(
        "http://localhost:8000/api/v1/review/contract",
        headers=headers,
        files={"file": f},
        data={"analysis_type": "comprehensive"}
    )
print(review_response.json())
```

---

## 🔧 JavaScript/TypeScript 客户端示例

```javascript
// 1. 登录
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});
const { access_token } = await loginResponse.json();

// 2. 文本翻译
const translateResponse = await fetch('http://localhost:8000/api/v1/translate/text', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: '你好，世界',
    source_lang: 'zh-Hans',
    target_lang: 'en',
    use_cloud: true
  })
});
const result = await translateResponse.json();
console.log(result);

// 3. 流式对话
const response = await fetch('http://localhost:8000/api/v1/chat/stream', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: '讲一个故事',
    model: 'gpt-4'
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const text = decoder.decode(value);
  console.log(text);
}
```

---

## 📊 API 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": "2024-11-20T12:00:00Z"
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "error",
  "error": "详细错误信息",
  "timestamp": "2024-11-20T12:00:00Z"
}
```

### 异步任务响应
```json
{
  "task_id": "task_abc123",
  "status": "processing",
  "message": "Task created successfully"
}
```

---

## 🎯 常用 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 (需要登录) |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

---

## 🔐 安全建议

1. **生产环境**:
   - 修改 `SECRET_KEY` 为强密码
   - 使用 HTTPS
   - 限制 CORS 来源
   - 实现 Token 黑名单机制

2. **速率限制**:
   - 建议添加 API 速率限制
   - 防止滥用

3. **日志记录**:
   - 记录所有 API 请求
   - 监控异常情况

---

## 📦 项目结构

```
/home/user/webapp/
├── api/                          # FastAPI 应用
│   ├── main.py                  # 主应用入口
│   ├── core/                    # 核心配置
│   │   ├── config.py           # 配置管理
│   │   └── security.py         # 安全认证
│   ├── routes/                  # API 路由
│   │   ├── auth.py             # 认证路由
│   │   ├── translate.py        # 翻译路由
│   │   ├── chat.py             # 对话路由
│   │   └── review.py           # 文档审查路由
│   ├── models/                  # 数据模型
│   │   ├── request.py          # 请求模型
│   │   └── response.py         # 响应模型
│   ├── services/                # 业务逻辑
│   │   └── translation_service.py
│   └── utils/                   # 工具函数
│       └── helpers.py
├── function/                     # 现有功能模块(复用)
├── streamlit_app.py             # Streamlit UI
└── requirements_api.txt         # API 依赖
```

---

## 🐛 故障排除

### 问题: Token 过期
**解决**: 使用 refresh token 刷新 access token

### 问题: 文件上传失败
**检查**: 文件大小是否超过 50MB，文件类型是否支持

### 问题: API 返回 500 错误
**检查**: 查看服务器日志，确认配置是否正确

---

## 📞 支持

- **API 文档**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs
- **项目文件**: `/home/user/webapp/api/`

---

## 🎓 下一步

1. ✅ **完成**: 基础 API 框架搭建
2. 🔄 **集成**: 与现有 Streamlit 功能深度集成
3. 📝 **扩展**: 添加更多 API 端点
4. 🚀 **部署**: Docker 容器化部署
5. 📊 **监控**: 添加日志和性能监控

---

**祝你使用愉快！🎉**
