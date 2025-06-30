"""
Query Processing Endpoints for LiveMind
Handles intelligent query processing with real-time data
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import logging
from datetime import datetime

from ...services.pathway_pipeline import pipeline
from ...services.vector_db import vector_db_service
from ...services.llm_service import llm_service

# Get logger
logger = logging.getLogger("livemind.query")

# Create router
router = APIRouter()

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    sources: Optional[List[str]] = ["news", "weather", "finance"]
    real_time: bool = True
    confidence_threshold: float = 0.7

class SourceInfo(BaseModel):
    name: str
    confidence: float
    timestamp: datetime
    url: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[SourceInfo]
    processing_time: float
    timestamp: datetime
    real_time_updates: bool

@router.post("/", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    🧠 Process intelligent query with real-time data
    
    This endpoint integrates:
    - Pathway real-time pipeline
    - Vector database semantic search  
    - Multi-source data fusion
    - Groq LLM processing (FREE!)
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Process query through our pipeline
        result = await pipeline.query_pipeline(
            query=request.query,
            sources=request.sources,
            top_k=10
        )
        
        # Extract sources information
        mock_sources = []
        for source_name in result.get('sources_used', []):
            mock_sources.append(SourceInfo(
                name=source_name,
                confidence=request.confidence_threshold,
                timestamp=datetime.now(),
                url=None
            ))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        response = QueryResponse(
            query=request.query,
            response=result.get('response', 'No response generated'),
            sources=mock_sources,
            processing_time=processing_time,
            timestamp=datetime.now(),
            real_time_updates=request.real_time
        )
        
        logger.info(f"Query processed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.get("/status")
async def query_status():
    """Get query system status"""
    try:
        pipeline_status = await pipeline.get_pipeline_status()
        return {
            "status": "active",
            "pipeline": pipeline_status,
            "services": {
                "pathway_pipeline": "active" if pipeline_status.get('pipeline_running') else "stopped",
                "vector_database": "ready",
                "llm_service": "ready",
                "real_time_updates": "active"
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/sources")
async def available_sources():
    """Get list of available data sources"""
    return {
        "sources": [
            {
                "name": "news",
                "description": "Real-time news feeds",
                "status": "available",
                "free_tier": True
            },
            {
                "name": "finance",
                "description": "Stock market and financial data",
                "status": "available", 
                "free_tier": True
            },
            {
                "name": "weather",
                "description": "Weather and environmental data",
                "status": "available",
                "free_tier": True
            },
            {
                "name": "social",
                "description": "Social media sentiment",
                "status": "coming_soon",
                "free_tier": True
            }
        ]
    }

@router.post("/pipeline/start")
async def start_pipeline():
    """🚀 Start the real-time pipeline"""
    try:
        await pipeline.initialize()
        pipeline.start_pipeline()
        return {
            "message": "Pipeline started successfully",
            "status": "running",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {str(e)}")

@router.post("/pipeline/stop") 
async def stop_pipeline():
    """🛑 Stop the real-time pipeline"""
    try:
        pipeline.stop_pipeline()
        return {
            "message": "Pipeline stopped successfully", 
            "status": "stopped",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop pipeline: {str(e)}")

@router.get("/pipeline/status")
async def get_pipeline_status():
    """📊 Get detailed pipeline status"""
    try:
        status = await pipeline.get_pipeline_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")

@router.get("/vector-db/stats")
async def get_vector_db_stats():
    """📈 Get vector database statistics"""
    try:
        stats = await vector_db_service.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get vector DB stats: {str(e)}")

@router.post("/data/refresh")
async def refresh_data_sources():
    """🔄 Manually refresh data from all sources"""
    try:
        from ...services.data_sources import data_source_manager
        
        # Fetch fresh data
        all_data = await data_source_manager.fetch_all_data()
        
        # Count total items
        total_items = sum(len(items) for items in all_data.values())
        
        return {
            "message": "Data refresh completed",
            "sources": {source: len(items) for source, items in all_data.items()},
            "total_items": total_items,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data refresh failed: {str(e)}")
