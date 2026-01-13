"""FastAPI application main entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.models.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="Groktor-X",
    description="Grok-powered search system for X posts",
    version="1.0.0",
    docs_url=None,  # Disable /docs
    redoc_url=None,  # Disable /redoc
    openapi_url=None  # Disable /openapi.json
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
        "version": "1.0.0"
    }

