"""
API Routes Configuration for LiveMind
Centralizes all API endpoint routing
"""

from fastapi import APIRouter
from .endpoints import query

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    query.router,
    prefix="/query",
    tags=["🧠 Intelligence Queries"]
)

# Health check route
@api_router.get("/", tags=["🏥 Health"])
async def api_root():
    """API root endpoint"""
    return {
        "message": "🧠 LiveMind API v1.0",
        "status": "active",
        "endpoints": {
            "query": "/api/v1/query/",
            "websocket": "/ws",
            "docs": "/docs"
        }
    }
