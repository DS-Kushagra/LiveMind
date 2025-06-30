"""
🤖 FREE LLM Service using Groq API
Lightning fast and completely FREE alternative to OpenAI!
"""

from groq import Groq
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import asyncio
import json
from datetime import datetime

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger("llm_service")

class GroqLLMService:
    """
    🚀 FREE & FAST LLM Service using Groq
    - Llama 3 model (completely free!)
    - Lightning fast responses
    - Streaming support
    - Context-aware processing
    """
    
    def __init__(self):
        self.client = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Groq client"""
        if self._initialized:
            return
        
        try:
            if not settings.GROQ_API_KEY:
                logger.warning("⚠️ Groq API key not configured. Using mock responses.")
                self._initialized = True
                return
            
            logger.info("🤖 Initializing Groq LLM Service...")
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            
            # Test the connection
            await self._test_connection()
            
            self._initialized = True
            logger.info("✅ Groq LLM Service initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq: {e}")
            logger.info("🔄 Falling back to mock mode")
            self._initialized = True
    
    async def _test_connection(self):
        """Test Groq API connection"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model=settings.GROQ_MODEL,
                max_tokens=10
            )
            logger.info("🔗 Groq API connection successful")
        except Exception as e:
            raise Exception(f"Groq API test failed: {e}")
    
    async def generate_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        sources: List[str] = None,
        stream: bool = False
    ) -> str:
        """
        🧠 Generate intelligent response using context
        
        Args:
            query: User query
            context: Relevant documents from vector DB
            sources: List of data sources used
            stream: Whether to stream response
        
        Returns:
            Generated response
        """
        if not self._initialized:
            await self.initialize()
        
        # If no API key, return mock response
        if not self.client:
            return await self._generate_mock_response(query, context, sources)
        
        try:
            # Build context-aware prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(query, context, sources)
            
            # Generate response using Groq
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=settings.GROQ_MODEL,
                max_tokens=1000,
                temperature=0.7,
                stream=stream
            )
            
            if stream:
                # Handle streaming response (for future WebSocket integration)
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"❌ Groq generation failed: {e}")
            return await self._generate_mock_response(query, context, sources)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for LiveMind"""
        return """You are LiveMind, a real-time multi-source intelligence AI assistant.

Your capabilities:
- Analyze real-time data from multiple sources (news, finance, weather, social media)
- Provide context-aware responses with source attribution
- Rate information confidence and highlight potential conflicts
- Offer predictive insights based on current trends

Guidelines:
- Always cite your sources and provide confidence levels
- Highlight when information conflicts between sources
- Be concise but comprehensive
- Use emojis sparingly for better readability
- If data is real-time, mention timestamps
- Distinguish between facts and analysis/predictions

You have access to real-time data and should provide current, accurate information."""
    
    def _build_user_prompt(
        self,
        query: str,
        context: List[Dict[str, Any]],
        sources: List[str] = None
    ) -> str:
        """Build user prompt with context"""
        prompt = f"User Query: {query}\n\n"
        
        if context:
            prompt += "Relevant Context from Real-Time Sources:\n"
            for i, ctx in enumerate(context, 1):
                metadata = ctx.get('metadata', {})
                confidence = ctx.get('confidence', 1.0)
                similarity = ctx.get('similarity', 1.0)
                
                prompt += f"\n{i}. Source: {metadata.get('source', 'unknown')}\n"
                prompt += f"   Confidence: {confidence:.2f}\n"
                prompt += f"   Relevance: {similarity:.2f}\n"
                prompt += f"   Timestamp: {metadata.get('timestamp', 'unknown')}\n"
                prompt += f"   Content: {ctx.get('content', '')[:500]}...\n"
        
        if sources:
            prompt += f"\nData Sources Available: {', '.join(sources)}\n"
        
        prompt += "\nPlease provide a comprehensive response using the above context. Include source attribution and confidence levels."
        
        return prompt
    
    async def _generate_mock_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        sources: List[str] = None
    ) -> str:
        """Generate mock response when API is not available"""
        
        context_summary = ""
        if context:
            context_summary = f" I found {len(context)} relevant pieces of information from sources like {', '.join(set(ctx.get('metadata', {}).get('source', 'unknown') for ctx in context[:3]))}."
        
        sources_info = ""
        if sources:
            sources_info = f" Available data sources: {', '.join(sources)}."
        
        return f"""🧠 **LiveMind Response** (Demo Mode)

**Query:** {query}

**Analysis:** {context_summary}{sources_info}

**Response:** This is a demonstration response. In production, LiveMind would analyze real-time data from multiple sources to provide intelligent, context-aware answers with source attribution and confidence scoring.

**Note:** Connect your Groq API key to enable full AI processing! 🚀

*Real-time features and multi-source intelligence will be fully functional once all services are connected.*"""
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        # Simple sentiment analysis (can be enhanced)
        positive_words = ['good', 'great', 'excellent', 'positive', 'bullish', 'up', 'growth']
        negative_words = ['bad', 'terrible', 'negative', 'bearish', 'down', 'decline', 'loss']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = max(0.2, 0.5 - (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": min(0.9, 0.6 + abs(positive_count - negative_count) * 0.1)
        }

# Global instance
llm_service = GroqLLMService()
