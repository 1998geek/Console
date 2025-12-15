"""
AIPortal FastAPI Main Application
Enterprise AI Services REST API
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import os

from .core.config import settings
from .routes import auth, translate, chat, review

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    print(f"🔐 Authentication: JWT with {settings.ALGORITHM}")
    
    yield
    
    # Shutdown
    print(f"👋 Shutting down {settings.APP_NAME}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## AIPortal REST API
    
    Enterprise AI services including:
    * 🌐 **Document Translation** - Multi-language document translation
    * 📄 **Document Review** - Contract and bidding document analysis  
    * 💬 **AI Chat** - Multi-model conversational AI
    * 🔐 **Authentication** - JWT-based security
    
    ### Quick Start
    
    1. **Login** to get access token: `POST /api/v1/auth/login`
    2. **Click the 'Authorize' button** at the top right (🔓)
    3. **Enter your token** in the format: `Bearer <your_access_token>` (or just the token)
    4. **Try protected endpoints** like `/api/v1/auth/me`
    
    ### Demo Credentials
    
    - **Admin**: username: `admin`, password: `admin123`
    - **User**: username: `user`, password: `user123`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,  # Keep authorization after page refresh
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request details
    print(f"\n{'='*60}")
    print(f"📥 {request.method} {request.url.path}")
    print(f"   Headers: {dict(request.headers)}")
    auth_header = request.headers.get("authorization")
    if auth_header:
        print(f"   Authorization: {auth_header[:50]}..." if len(auth_header) > 50 else f"   Authorization: {auth_header}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    print(f"📤 {request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    print(f"{'='*60}\n")
    
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "Validation error",
            "errors": exc.errors(),
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred",
            "timestamp": time.time()
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": settings.API_V1_PREFIX
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


# Register routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(translate.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(review.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
