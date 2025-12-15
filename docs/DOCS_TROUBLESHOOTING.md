# 📖 API 文档访问指南

## 🎯 可用的文档界面

你的 FastAPI 应用提供了 **3 种** 文档访问方式：

### 1. 📘 Swagger UI (推荐)
**最佳交互式文档**，可以直接在浏览器中测试 API

🔗 **访问地址**: 
```
https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs
```

**特点**:
- ✅ 可以直接测试 API
- ✅ 实时查看请求/响应
- ✅ 支持 Token 认证
- ✅ 交互式表单
- ✅ 加载速度快

**如何使用**:
1. 打开上面的链接
2. 点击任意 API 端点
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute" 执行请求

---

### 2. 📗 ReDoc
**美观的静态文档**，适合阅读和学习 API 结构

🔗 **访问地址**:
```
https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/redoc
```

**特点**:
- ✅ 界面美观
- ✅ 三栏布局
- ✅ 代码示例
- ✅ 搜索功能
- ⚠️ 需要从 CDN 加载资源（可能较慢）

**加载问题排查**:
如果 ReDoc 页面显示空白：

1. **等待加载** - ReDoc 需要从 CDN (jsdelivr) 加载 JavaScript，首次访问可能需要 10-30 秒
2. **检查网络** - 确保可以访问 `cdn.jsdelivr.net`
3. **刷新页面** - 按 F5 或 Ctrl+R 刷新
4. **清除缓存** - Ctrl+Shift+R 强制刷新
5. **使用 Swagger** - 如果 ReDoc 无法加载，使用 Swagger UI 替代

**常见原因**:
- CDN 资源加载较慢
- 网络防火墙阻止外部资源
- 浏览器 JavaScript 被禁用

---

### 3. 📄 OpenAPI JSON/YAML
**原始 API 规范**，可用于生成客户端代码

🔗 **访问地址**:
```
# JSON 格式
https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/openapi.json

# YAML 格式 (如果需要)
https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/openapi.yaml
```

**用途**:
- 使用工具生成客户端代码
- 导入 Postman/Insomnia
- 自动化测试
- 集成到 CI/CD

---

## 🚀 推荐使用方式

### 对于新用户（学习和测试）
👉 **使用 Swagger UI**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs

**原因**:
- 可以直接测试，无需编写代码
- 实时查看结果
- 支持文件上传
- 加载快速稳定

### 对于开发者（集成和调试）
👉 **使用以下工具**:

1. **Postman/Insomnia** - 导入 OpenAPI JSON
2. **cURL** - 命令行测试
3. **Python requests** - 编程调用

### 对于阅读文档
👉 **使用 ReDoc** (如果加载成功)

---

## 🔧 快速测试步骤

### 使用 Swagger UI

1. **打开文档**
   ```
   https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs
   ```

2. **登录获取 Token**
   - 找到 `POST /api/v1/auth/login`
   - 点击 "Try it out"
   - 输入:
     ```json
     {
       "username": "admin",
       "password": "admin123"
     }
     ```
   - 点击 "Execute"
   - 复制返回的 `access_token`

3. **设置认证**
   - 点击页面右上角的 🔓 "Authorize" 按钮
   - 输入: `Bearer YOUR_ACCESS_TOKEN`
   - 点击 "Authorize"
   - 点击 "Close"

4. **测试 API**
   - 现在所有 API 都已认证
   - 选择任意端点测试
   - 例如: `POST /api/v1/translate/text`

---

## 📱 其他访问方式

### 使用 cURL

```bash
# 1. 登录
TOKEN=$(curl -s -X POST \
  "https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. 调用 API
curl -X POST \
  "https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/api/v1/translate/text" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，世界",
    "source_lang": "zh-Hans",
    "target_lang": "en"
  }'
```

### 使用 Python

```python
import requests

# 1. 登录
response = requests.post(
    "https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/api/v1/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# 2. 调用 API
headers = {"Authorization": f"Bearer {token}"}
result = requests.post(
    "https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/api/v1/translate/text",
    headers=headers,
    json={
        "text": "你好，世界",
        "source_lang": "zh-Hans",
        "target_lang": "en"
    }
)
print(result.json())
```

---

## ❓ 常见问题

### Q1: ReDoc 页面空白？
**A**: ReDoc 依赖 CDN 加载资源，可能需要等待 10-30 秒。建议使用 Swagger UI 替代。

### Q2: 如何测试文件上传？
**A**: 在 Swagger UI 中，选择文件上传的端点（如 `/api/v1/translate/document`），点击 "Try it out"，会出现文件选择按钮。

### Q3: 401 Unauthorized 错误？
**A**: 
1. 确保已登录获取 Token
2. 在 Swagger UI 中点击 "Authorize" 设置 Token
3. 或在请求头中添加: `Authorization: Bearer YOUR_TOKEN`

### Q4: Token 过期了？
**A**: 使用 `POST /api/v1/auth/refresh` 刷新 Token，或重新登录。

### Q5: 如何测试流式响应？
**A**: 流式端点（`/api/v1/chat/stream`）在浏览器中会下载文件，建议使用 cURL 或编程方式测试：
```bash
curl -N -X POST \
  "https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/api/v1/chat/stream" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"讲个故事","model":"gpt-4"}'
```

---

## 📊 文档对比

| 特性 | Swagger UI | ReDoc | OpenAPI JSON |
|------|-----------|-------|--------------|
| 交互测试 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| 界面美观 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ 无界面 |
| 加载速度 | 快 | 较慢 (CDN) | 最快 |
| 文件上传 | ✅ 支持 | ❌ 不支持 | N/A |
| 认证测试 | ✅ 支持 | ❌ 不支持 | N/A |
| 代码示例 | 有 | 更详细 | 需工具生成 |
| 搜索功能 | ✅ | ✅ | N/A |
| 离线使用 | ✅ | ⚠️ 需CDN | ✅ |

**结论**: 👉 **推荐使用 Swagger UI** 进行日常测试和开发

---

## 🎯 最佳实践

1. **开发测试**: 使用 Swagger UI
2. **学习文档**: 使用 ReDoc (如能加载)
3. **自动化**: 使用 OpenAPI JSON 生成客户端
4. **生产环境**: 使用编程方式调用 API

---

## 🔗 相关链接

- **Swagger UI**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/docs ⭐
- **ReDoc**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/redoc
- **OpenAPI JSON**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/openapi.json
- **API 根路径**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/
- **健康检查**: https://8000-if117d3ltnvxax5y34ynw-b9b802c4.sandbox.novita.ai/health

---

**需要帮助？** 查看 [API_USAGE_GUIDE.md](./API_USAGE_GUIDE.md) 获取详细使用说明。
