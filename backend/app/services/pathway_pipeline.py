"""
🔄 Pathway Real-Time Processing Pipeline for LiveMind
The CORE of our real-time intelligence system!
"""

import pathway as pw
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import threading
import time

from ..core.config import settings
from ..core.logging import get_logger
from .vector_db import vector_db_service
from .data_sources import data_source_manager

logger = get_logger("pathway_pipeline")

class LiveMindPipeline:
    """
    🧠 Real-Time Intelligence Pipeline using Pathway
    
    Features:
    - Real-time data ingestion from multiple sources
    - Automatic embedding generation and vector storage
    - Change detection and updates
    - Source confidence scoring
    """
    
    def __init__(self):
        self.pipeline_running = False
        self.pipeline_thread = None
        self.data_sources = data_source_manager
        self.vector_db = vector_db_service
        
    async def initialize(self):
        """Initialize the pipeline"""
        try:
            logger.info("🔄 Initializing Pathway Pipeline...")
            
            # Initialize dependencies
            await self.data_sources.initialize_all()
            await self.vector_db.initialize()
            
            logger.info("✅ Pathway Pipeline initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Pipeline initialization failed: {e}")
            raise
    
    def start_pipeline(self):
        """Start the real-time pipeline in background"""
        if self.pipeline_running:
            logger.warning("Pipeline already running")
            return
        
        logger.info("🚀 Starting Pathway real-time pipeline...")
        self.pipeline_running = True
        
        # Start pipeline in separate thread to avoid blocking
        self.pipeline_thread = threading.Thread(
            target=self._run_pipeline_loop,
            daemon=True
        )
        self.pipeline_thread.start()
        
        logger.info("✅ Pipeline started successfully!")
    
    def stop_pipeline(self):
        """Stop the real-time pipeline"""
        if not self.pipeline_running:
            return
        
        logger.info("🛑 Stopping pipeline...")
        self.pipeline_running = False
        
        if self.pipeline_thread:
            self.pipeline_thread.join(timeout=5)
        
        logger.info("✅ Pipeline stopped")
    
    def _run_pipeline_loop(self):
        """Main pipeline loop - runs in background thread"""
        logger.info("🔄 Pipeline loop started")
        
        # Create event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.pipeline_running:
                try:
                    # Run one pipeline cycle
                    loop.run_until_complete(self._pipeline_cycle())
                    
                    # Wait before next cycle (configurable)
                    time.sleep(60)  # 1 minute intervals for demo
                    
                except Exception as e:
                    logger.error(f"❌ Pipeline cycle error: {e}")
                    time.sleep(30)  # Wait before retry
                    
        except Exception as e:
            logger.error(f"❌ Pipeline loop error: {e}")
        finally:
            loop.close()
            logger.info("🔄 Pipeline loop ended")
    
    async def _pipeline_cycle(self):
        """One complete pipeline processing cycle"""
        try:
            logger.info("🔄 Running pipeline cycle...")
            
            # Fetch fresh data from all sources
            all_data = await self.data_sources.fetch_all_data()
            
            processed_count = 0
            
            # Process each data source
            for source_name, data_items in all_data.items():
                if not data_items:
                    continue
                    
                logger.info(f"📊 Processing {len(data_items)} items from {source_name}")
                
                for item in data_items:
                    try:
                        await self._process_data_item(item, source_name)
                        processed_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to process item: {e}")
                        continue
            
            logger.info(f"✅ Pipeline cycle completed: {processed_count} items processed")
            
        except Exception as e:
            logger.error(f"❌ Pipeline cycle failed: {e}")
    
    async def _process_data_item(self, item: Dict[str, Any], source: str):
        """Process a single data item through the pipeline"""
        try:
            # Extract text content for embedding
            content = self._extract_content(item)
            if not content:
                return
            
            # Calculate confidence score
            confidence = self._calculate_confidence(item, source)
            
            # Prepare metadata
            metadata = {
                "source": source,
                "original_data": json.dumps(item, default=str),
                "processed_at": datetime.now().isoformat(),
                **{k: v for k, v in item.items() if k not in ['content', 'title', 'summary']}
            }
            
            # Add to vector database
            await self.vector_db.add_document(
                content=content,
                source=source,
                metadata=metadata,
                confidence=confidence
            )
            
        except Exception as e:
            logger.warning(f"Failed to process data item: {e}")
    
    def _extract_content(self, item: Dict[str, Any]) -> str:
        """Extract meaningful text content from data item"""
        content_parts = []
        
        # Extract title/headline
        if 'title' in item:
            content_parts.append(item['title'])
        
        # Extract summary/description
        if 'summary' in item:
            content_parts.append(item['summary'])
        elif 'content' in item:
            content_parts.append(item['content'])
        elif 'description' in item:
            content_parts.append(item['description'])
        
        # For financial data, include key metrics
        if item.get('content_type') == 'stock_data':
            symbol = item.get('symbol', '')
            price = item.get('price', 0)
            change = item.get('change_percent', 0)
            content_parts.append(f"{symbol} stock trading at ${price}, {change:+.2f}% change")
        
        # For weather data, include conditions
        elif item.get('content_type') == 'weather_data':
            city = item.get('city', '')
            temp = item.get('temperature', 0)
            desc = item.get('description', '')
            content_parts.append(f"Weather in {city}: {temp}°C, {desc}")
        
        return " | ".join(filter(None, content_parts))
    
    def _calculate_confidence(self, item: Dict[str, Any], source: str) -> float:
        """Calculate confidence score for data item"""
        base_confidence = {
            'news': 0.8,
            'reddit': 0.6,
            'finance': 0.9,
            'weather': 0.95
        }.get(source, 0.7)
        
        # Adjust based on item properties
        if source == 'reddit':
            score = item.get('score', 0)
            comments = item.get('comments', 0)
            # Higher score/comments = higher confidence
            if score > 100 or comments > 50:
                base_confidence += 0.1
            elif score < 10:
                base_confidence -= 0.1
        
        elif source == 'news':
            # Newer articles get higher confidence
            published = item.get('published', '')
            if published:
                # Simple recency boost (this could be more sophisticated)
                base_confidence += 0.05
        
        return max(0.1, min(1.0, base_confidence))
    
    async def query_pipeline(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        🔍 Query the pipeline for intelligent responses
        
        This is the main interface for getting AI responses
        """
        try:
            logger.info(f"🔍 Processing query: {query}")
            start_time = datetime.now()
            
            # Search for relevant context in vector database
            context_docs = await self.vector_db.search_similar(
                query=query,
                top_k=top_k,
                sources=sources
            )
            
            # Get AI response using context
            from .llm_service import llm_service
            response = await llm_service.generate_response(
                query=query,
                context=context_docs,
                sources=sources
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "query": query,
                "response": response,
                "context_sources": len(context_docs),
                "processing_time": processing_time,
                "sources_used": list(set(doc.get('metadata', {}).get('source', 'unknown') for doc in context_docs)),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Query processed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            return {
                "query": query,
                "response": f"Sorry, I encountered an error processing your query: {str(e)}",
                "error": True,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        try:
            vector_stats = await self.vector_db.get_collection_stats()
            
            return {
                "pipeline_running": self.pipeline_running,
                "vector_db_documents": vector_stats.get('total_documents', 0),
                "data_sources": {
                    "news": "active",
                    "reddit": "active",
                    "finance": "active", 
                    "weather": "active"
                },
                "last_update": datetime.now().isoformat(),
                "status": "healthy" if self.pipeline_running else "stopped"
            }
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            return {"status": "error", "error": str(e)}

# Global pipeline instance
pipeline = LiveMindPipeline()
