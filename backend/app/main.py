"""FastAPI application main entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.models.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="X AI Search API",
    description="Grok-powered search system for X (Twitter) posts",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("🚀 X AI Search API started")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "X AI Search API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "post": "/api/posts/{post_id}",
            "list": "/api/posts",
            "stats": "/api/stats",
            "health": "/health",
            "docs": "/docs"
        }
    }

