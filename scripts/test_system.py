"""
Test script to validate the AI Trip Agent setup.
Tests LLM connectivity, vector store, and agent workflow.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_settings
from config.llm_adapter import LLMAdapter
from services.rag.embeddings import EmbeddingManager
from services.rag.vector_store import VectorStoreManager
from services.carbon import CarbonCalculator, TransportMode
from agents import create_agent_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_configuration():
    """Test configuration loading."""
    logger.info("=" * 60)
    logger.info("Testing Configuration")
    logger.info("=" * 60)
    
    try:
        settings = get_settings()
        logger.info(f"✅ Configuration loaded successfully")
        logger.info(f"   LLM Provider: {settings.llm_provider.value}")
        logger.info(f"   ChromaDB: {settings.get_chroma_url()}")
        logger.info(f"   Environment: {settings.environment}")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False


def test_llm_connection():
    """Test LLM connectivity."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing LLM Connection")
    logger.info("=" * 60)
    
    try:
        settings = get_settings()
        llm_adapter = LLMAdapter(settings)
        llm = llm_adapter.get_llm()
        
        # Test simple invocation
        response = llm.invoke("Say 'Hello' in one word.")
        logger.info(f"✅ LLM connection successful")
        logger.info(f"   Provider: {settings.llm_provider.value}")
        logger.info(f"   Response: {response.content[:100]}")
        return True
    except Exception as e:
        logger.error(f"❌ LLM connection test failed: {e}")
        return False


def test_embeddings():
    """Test embedding generation."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Embeddings")
    logger.info("=" * 60)
    
    try:
        settings = get_settings()
        embedding_manager = EmbeddingManager(settings)
        
        # Test embedding
        test_text = "Kaziranga National Park is famous for one-horned rhinoceros."
        embedding = embedding_manager.embed_query(test_text)
        
        logger.info(f"✅ Embeddings working")
        logger.info(f"   Provider: {settings.embedding_provider}")
        logger.info(f"   Embedding dimension: {len(embedding)}")
        return True
    except Exception as e:
        logger.error(f"❌ Embeddings test failed: {e}")
        return False


def test_vector_store():
    """Test vector store connectivity."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Vector Store")
    logger.info("=" * 60)
    
    try:
        settings = get_settings()
        embedding_manager = EmbeddingManager(settings)
        vector_store_manager = VectorStoreManager(settings, embedding_manager)
        
        # Test connection
        client = vector_store_manager.get_client()
        client.heartbeat()
        
        # Get stats
        stats = vector_store_manager.get_collection_stats()
        
        logger.info(f"✅ Vector store connected")
        logger.info(f"   Collection: {stats.get('name')}")
        logger.info(f"   Document count: {stats.get('count', 0)}")
        
        if stats.get('count', 0) == 0:
            logger.warning("   ⚠️  No documents in vector store. Run seed script first.")
        
        return True
    except Exception as e:
        logger.error(f"❌ Vector store test failed: {e}")
        logger.info("   Make sure ChromaDB is running:")
        logger.info("   docker run -d -p 8002:8000 -v ./chroma_data:/chroma chromadb/chroma:latest")
        return False


def test_carbon_calculator():
    """Test carbon calculation."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Carbon Calculator")
    logger.info("=" * 60)
    
    try:
        calculator = CarbonCalculator()
        
        # Test calculation
        result = calculator.calculate(
            distance_km=200,
            transport_mode=TransportMode.CAR_PETROL
        )
        
        logger.info(f"✅ Carbon calculator working")
        logger.info(f"   Distance: {result.distance_km} km")
        logger.info(f"   Emissions: {result.total_emissions_kg:.2f} kg CO2e")
        logger.info(f"   Tree equivalent: {result.equivalent_trees:.1f} trees")
        return True
    except Exception as e:
        logger.error(f"❌ Carbon calculator test failed: {e}")
        return False


def test_agent_workflow():
    """Test complete agent workflow."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Agent Workflow")
    logger.info("=" * 60)
    
    try:
        settings = get_settings()
        llm_adapter = LLMAdapter(settings)
        llm = llm_adapter.get_llm()
        
        embedding_manager = EmbeddingManager(settings)
        vector_store_manager = VectorStoreManager(settings, embedding_manager)
        carbon_calculator = CarbonCalculator()
        
        # Create agent graph
        agent_graph = create_agent_graph(llm, vector_store_manager, carbon_calculator)
        
        # Test with simple query
        test_query = "Plan a 2-day trip to Kaziranga for wildlife viewing"
        
        logger.info(f"   Test query: {test_query}")
        
        initial_state = {
            "user_query": test_query,
            "messages": [],
            "transport_mode": "car_petrol",
            "retrieved_docs": [],
            "interests": [],
            "green_alternatives": [],
            "recommendations": [],
            "should_continue": True,
        }
        
        # Run workflow
        final_state = agent_graph.invoke(initial_state)
        
        logger.info(f"✅ Agent workflow completed")
        logger.info(f"   Destination: {final_state.get('destination')}")
        logger.info(f"   Duration: {final_state.get('duration_days')} days")
        logger.info(f"   Messages: {len(final_state.get('messages', []))}")
        
        if final_state.get('error'):
            logger.warning(f"   ⚠️  Workflow error: {final_state['error']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Agent workflow test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 60)
    logger.info("AI TRIP AGENT - SYSTEM VALIDATION")
    logger.info("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("LLM Connection", test_llm_connection),
        ("Embeddings", test_embeddings),
        ("Vector Store", test_vector_store),
        ("Carbon Calculator", test_carbon_calculator),
        ("Agent Workflow", test_agent_workflow),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready.")
        return 0
    else:
        logger.warning("⚠️  Some tests failed. Please check the logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
