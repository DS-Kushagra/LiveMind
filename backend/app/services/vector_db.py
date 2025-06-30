"""
🧠 Vector Database Service for LiveMind
Using ChromaDB for FREE local vector storage with semantic search
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Dict, Any, Optional
import asyncio
import hashlib
from datetime import datetime
import json

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger("vector_db")

class VectorDatabaseService:
    """
    🎯 FREE Vector Database Service using ChromaDB
    - Local storage (no cloud costs!)
    - Fast semantic search
    - Source attribution and confidence scoring
    - Real-time updates
    """
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedder = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize ChromaDB and embedding model"""
        if self._initialized:
            return
        
        try:
            logger.info("🧠 Initializing Vector Database Service...")
            
            # Initialize ChromaDB with persistence
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collection
            collection_name = "livemind_intelligence"
            try:
                self.collection = self.client.get_collection(collection_name)
                logger.info(f"📂 Loaded existing collection: {collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": "LiveMind real-time intelligence data"}
                )
                logger.info(f"📂 Created new collection: {collection_name}")
            
            # Initialize embedding model (free and fast!)
            logger.info("🤖 Loading embedding model...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast, free!
            
            self._initialized = True
            logger.info("✅ Vector Database Service initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vector Database: {e}")
            raise
    
    def _generate_doc_id(self, content: str, source: str) -> str:
        """Generate unique document ID"""
        combined = f"{source}:{content[:100]}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    async def add_document(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> str:
        """
        🔄 Add document to vector database
        
        Args:
            content: Text content to embed
            source: Source name (news, reddit, etc.)
            metadata: Additional metadata
            confidence: Source confidence score (0-1)
        
        Returns:
            Document ID
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Generate embedding
            embedding = self.embedder.encode(content).tolist()
            
            # Create document ID
            doc_id = self._generate_doc_id(content, source)
            
            # Prepare metadata
            doc_metadata = {
                "source": source,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                **(metadata or {})
            }
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            logger.debug(f"📝 Added document: {doc_id[:8]}... from {source}")
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add document: {e}")
            raise
    
    async def search_similar(
        self,
        query: str,
        top_k: int = 5,
        min_confidence: float = 0.5,
        sources: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        🔍 Search for similar documents using semantic search
        
        Args:
            query: Search query
            top_k: Number of results to return
            min_confidence: Minimum confidence threshold
            sources: Filter by specific sources
        
        Returns:
            List of similar documents with metadata
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Build where clause for filtering
            where_clause = {}
            if min_confidence > 0:
                where_clause["confidence"] = {"$gte": min_confidence}
            if sources:
                where_clause["source"] = {"$in": sources}
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        "content": doc,
                        "metadata": results['metadatas'][0][i],
                        "similarity": 1 - results['distances'][0][i],  # Convert distance to similarity
                        "confidence": results['metadatas'][0][i].get('confidence', 1.0)
                    }
                    formatted_results.append(result)
            
            logger.debug(f"🔍 Found {len(formatted_results)} similar documents for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        if not self._initialized:
            await self.initialize()
        
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name,
                "embedding_model": "all-MiniLM-L6-v2",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {}
    
    async def delete_old_documents(self, days_old: int = 7):
        """Delete documents older than specified days"""
        # Implementation for cleanup (optional for demo)
        pass

# Global instance
vector_db_service = VectorDatabaseService()
