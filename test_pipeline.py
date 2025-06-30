# 🧪 LiveMind Pipeline Test Script
# Test the real-time intelligence pipeline!

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

async def test_pipeline():
    """Test the complete pipeline functionality"""
    print("🧠 Testing LiveMind Real-Time Pipeline")
    print("=" * 50)
    
    try:
        # Import services
        from backend.app.services.pathway_pipeline import pipeline
        from backend.app.services.vector_db import vector_db_service
        from backend.app.services.llm_service import llm_service
        from backend.app.services.data_sources import data_source_manager
        
        # Test 1: Initialize Pipeline
        print("\n🔄 Test 1: Pipeline Initialization")
        await pipeline.initialize()
        print("✅ Pipeline initialized successfully!")
        
        # Test 2: Vector Database
        print("\n🧠 Test 2: Vector Database")
        await vector_db_service.add_document(
            content="Tesla stock is performing well with strong earnings",
            source="test",
            metadata={"test": True},
            confidence=0.9
        )
        
        results = await vector_db_service.search_similar("Tesla stock performance")
        print(f"✅ Vector DB working! Found {len(results)} similar documents")
        
        # Test 3: Data Sources
        print("\n📡 Test 3: Data Sources")
        news_data = await data_source_manager.news_source.fetch_latest_news(limit=2)
        print(f"✅ News: Fetched {len(news_data)} articles")
        
        finance_data = await data_source_manager.finance_source.fetch_stock_data(['AAPL'])
        print(f"✅ Finance: Fetched {len(finance_data)} stock data points")
        
        # Test 4: LLM Service
        print("\n🤖 Test 4: LLM Service")
        response = await llm_service.generate_response(
            query="What's happening with technology stocks?",
            context=[{"content": "Tech stocks are rising", "metadata": {"source": "test"}}]
        )
        print(f"✅ LLM Response: {response[:100]}...")
        
        # Test 5: Complete Query Processing
        print("\n🔍 Test 5: End-to-End Query")
        query_result = await pipeline.query_pipeline(
            query="Tell me about recent market trends",
            top_k=3
        )
        print(f"✅ Query processed in {query_result.get('processing_time', 0):.2f}s")
        print(f"Response: {query_result.get('response', '')[:100]}...")
        
        # Test 6: Pipeline Status
        print("\n📊 Test 6: Pipeline Status")
        status = await pipeline.get_pipeline_status()
        print(f"✅ Pipeline Status: {status.get('status', 'unknown')}")
        print(f"Documents in Vector DB: {status.get('vector_db_documents', 0)}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 LiveMind pipeline is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def demo_queries():
    """Run some demo queries to show capabilities"""
    print("\n🎪 Demo Queries")
    print("=" * 30)
    
    demo_queries = [
        "What's happening with Tesla stock?",
        "Tell me about recent technology news",
        "What's the weather like in major cities?",
        "What are people discussing on Reddit?"
    ]
    
    from backend.app.services.pathway_pipeline import pipeline
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Demo {i}: {query}")
        try:
            result = await pipeline.query_pipeline(query, top_k=3)
            print(f"⚡ Response ({result.get('processing_time', 0):.2f}s):")
            print(f"📝 {result.get('response', 'No response')[:200]}...")
            print(f"📊 Sources used: {', '.join(result.get('sources_used', []))}")
        except Exception as e:
            print(f"❌ Query failed: {e}")

def main():
    print("🧠 LiveMind Pipeline Testing Suite")
    print("🔧 Make sure you're in the LiveMind root directory")
    
    if not os.path.exists("backend"):
        print("❌ Backend directory not found. Run from LiveMind root directory.")
        return
    
    # Run tests
    success = asyncio.run(test_pipeline())
    
    if success:
        print("\n" + "="*50)
        choice = input("🎪 Run demo queries? (y/n): ").lower().strip()
        if choice == 'y':
            asyncio.run(demo_queries())
    
    print("\n🧠 Testing complete!")
    print("💡 Next steps:")
    print("   1. Set up your free API keys in .env")
    print("   2. Run: python -m uvicorn main:app --reload")
    print("   3. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
