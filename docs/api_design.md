# AIPortal REST API 设计方案

## 技术选型
- **框架**: FastAPI (推荐)
- **异步**: async/await
- **文档**: 自动生成 OpenAPI/Swagger
- **认证**: JWT Token
- **部署**: Docker + Nginx

---

## API 模块设计

### 1. 文档翻译 API
```
POST /api/v1/translate/document
- 上传文档进行翻译
- 支持格式: docx, pptx, xlsx, pdf
- 参数: file, source_lang, target_lang, use_cloud

GET /api/v1/translate/status/{task_id}
- 查询翻译任务状态

GET /api/v1/translate/download/{task_id}
- 下载翻译后的文档
```

### 2. 文档审查 API
```
POST /api/v1/review/contract
- 合同智能初审
- 返回: 风险点、建议、评分

POST /api/v1/review/bidding
- 标书智能审查
- 返回: 合规性检查、问题列表

POST /api/v1/review/compare
- Word 文档比对
- 返回: 差异列表、修改建议
```

### 3. 智能对话 API
```
POST /api/v1/chat/completion
- 多模型问答
- 支持流式输出
- 参数: message, model, history, stream

POST /api/v1/chat/multimodal
- 多模态问答
- 支持图片+文字输入

POST /api/v1/dify/chat
- Dify 智能体集成
```

### 4. 图像识别 API
```
POST /api/v1/vision/detect-violation
- 员工违规操作识别
- 返回: 检测结果、置信度、标注图
```

### 5. 数据查询 API
```
POST /api/v1/bi/query
- 智能问数 (Text-to-SQL)
- 返回: SQL、执行结果、图表数据

GET /api/v1/case/search
- 案例查询
- 参数: keyword, filters, limit

POST /api/v1/research/customer
- 客户背景调研
- 返回: 客户信息、风险评估
```

### 6. 视频生成 API
```
POST /api/v1/video/generate
- Sora 视频生成
- 异步任务，返回 task_id

GET /api/v1/video/status/{task_id}
- 查询生成状态

GET /api/v1/video/download/{task_id}
- 下载生成的视频
```

### 7. 工具类 API
```
POST /api/v1/tools/word/format
- Word 文档整理（标题编号等）

POST /api/v1/tools/email/send
- 发送邮件

POST /api/v1/tools/blob/upload
- 上传文件到 Azure Blob
```

### 8. 配置管理 API
```
GET /api/v1/config/prompts
- 获取 Prompt 配置

PUT /api/v1/config/prompts/{id}
- 更新 Prompt 配置

GET /api/v1/config/newsletter
- 获取 AI 简报设置
```

### 9. 用户认证 API
```
POST /api/v1/auth/login
- 用户登录
- 返回: access_token, refresh_token

POST /api/v1/auth/refresh
- 刷新 Token

POST /api/v1/auth/logout
- 登出

GET /api/v1/auth/me
- 获取当前用户信息
```

---

## 数据格式规范

### 统一响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": "2024-11-20T12:00:00Z"
}
```

### 错误响应格式
```json
{
  "code": 400,
  "message": "Invalid parameters",
  "error": "source_lang is required",
  "timestamp": "2024-11-20T12:00:00Z"
}
```

---

## 技术实现要点

### 1. 异步处理长时间任务
```python
from fastapi import BackgroundTasks
from celery import Celery

# 方案1: FastAPI BackgroundTasks (简单任务)
@app.post("/api/v1/translate/document")
async def translate_doc(file: UploadFile, background_tasks: BackgroundTasks):
    task_id = generate_task_id()
    background_tasks.add_task(process_translation, task_id, file)
    return {"task_id": task_id, "status": "processing"}

# 方案2: Celery (复杂任务，需要分布式)
celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def process_translation(task_id, file_path):
    # 执行翻译
    pass
```

### 2. 文件上传处理
```python
@app.post("/api/v1/upload")
async def upload_file(file: UploadFile):
    # 保存到临时目录
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 或者直接上传到 Azure Blob
    blob_client.upload_blob(content)
    return {"filename": file.filename}
```

### 3. 流式输出 (SSE)
```python
from fastapi.responses import StreamingResponse

@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        async for chunk in ai_client.stream_chat(request.message):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 4. 认证中间件
```python
from fastapi import Depends, HTTPException, Header
import jwt

def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing token")
    
    try:
        token = authorization.split(" ")[1]  # Bearer <token>
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(401, "Invalid token")

@app.get("/api/v1/protected")
async def protected_route(user = Depends(verify_token)):
    return {"user": user}
```

---

## 部署架构

```
                           ┌─────────────┐
                           │   Nginx     │
                           │  (反向代理)  │
                           └──────┬──────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
              ┌─────▼──────┐            ┌──────▼──────┐
              │  FastAPI   │            │  Streamlit  │
              │   (API)    │            │    (UI)     │
              │  Port 8000 │            │  Port 8501  │
              └─────┬──────┘            └─────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
   ┌────▼───┐  ┌───▼────┐  ┌──▼─────┐
   │ Redis  │  │PostgreSQL│ │ Azure  │
   │(Cache) │  │   (DB)   │ │Services│
   └────────┘  └──────────┘ └────────┘
```

---

## 项目结构建议

```
/home/user/webapp/
├── api/                      # FastAPI 应用
│   ├── __init__.py
│   ├── main.py              # FastAPI app 入口
│   ├── routes/              # 路由模块
│   │   ├── translate.py
│   │   ├── review.py
│   │   ├── chat.py
│   │   └── ...
│   ├── models/              # Pydantic 模型
│   │   ├── request.py
│   │   └── response.py
│   ├── services/            # 业务逻辑
│   │   ├── translation_service.py
│   │   ├── review_service.py
│   │   └── ...
│   ├── middleware/          # 中间件
│   │   └── auth.py
│   └── utils/               # 工具函数
│       └── helpers.py
├── function/                # 现有的功能模块（复用）
├── sub_pages/               # Streamlit UI（保留）
├── streamlit_app.py         # Streamlit 入口
├── requirements_api.txt     # API 依赖
└── docker-compose.yml       # Docker 编排
```

---

## 迁移策略

### 阶段1: 核心功能 API 化 (2周)
- 文档翻译 API
- 文档审查 API
- 认证系统

### 阶段2: 智能对话 API 化 (2周)
- 多模型问答
- Dify/XInference 集成
- 流式输出支持

### 阶段3: 高级功能 API 化 (2周)
- 图像识别
- 视频生成
- BI 查询

### 阶段4: 优化和部署 (1周)
- 性能优化
- 缓存策略
- 监控告警
- 文档完善

---

## 性能优化建议

1. **Redis 缓存**: 缓存频繁查询的结果
2. **连接池**: 数据库、Azure 服务使用连接池
3. **异步 IO**: 所有 IO 操作使用 async/await
4. **限流**: 使用 slowapi 限制请求频率
5. **CDN**: 静态资源使用 CDN
6. **负载均衡**: 多实例部署 + Nginx 负载均衡

---

## 监控和日志

```python
# 使用 structlog 结构化日志
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("request_received", 
                method=request.method, 
                path=request.url.path)
    
    response = await call_next(request)
    
    logger.info("request_completed", 
                status_code=response.status_code)
    
    return response
```

---

## 总结

将 Streamlit 功能封装成 REST API 的优势：
- ✅ 更好的扩展性和性能
- ✅ 支持多端访问
- ✅ 便于集成到现有系统
- ✅ 微服务架构友好
- ✅ 独立测试和部署

**建议**: 保留 Streamlit UI 作为快速原型和内部工具，同时提供 REST API 供外部系统和移动端使用。
