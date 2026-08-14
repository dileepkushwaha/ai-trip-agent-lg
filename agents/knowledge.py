"""
Knowledge Agent - Retrieves relevant information from vector store.
"""

import logging
from typing import Dict, Any, List

from langchain_core.messages import AIMessage

from agents.state import AgentState
from services.rag.vector_store import VectorStoreManager

logger = logging.getLogger(__name__)


class KnowledgeAgent:
    """Agent responsible for retrieving relevant local knowledge."""
    
    def __init__(self, vector_store_manager: VectorStoreManager):
        """Initialize knowledge agent with vector store."""
        self.vector_store = vector_store_manager
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge from vector store.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with retrieved documents
        """
        try:
            destination = state.get("destination", "Assam")
            interests = state.get("interests", [])
            user_query = state.get("user_query", "")
            
            logger.info(f"Retrieving knowledge for: {destination}")
            
            # Build search query
            search_query = self._build_search_query(destination, interests, user_query)
            
            # Retrieve documents
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query=search_query,
                k=5
            )
            
            if not docs_with_scores:
                logger.warning("No relevant documents found")
                return {
                    "retrieved_docs": [],
                    "local_knowledge": "Limited information available for this destination.",
                    "next_agent": "itinerary",
                    "should_continue": True,
                }
            
            # Format retrieved documents
            retrieved_docs = []
            knowledge_parts = []
            
            for doc, score in docs_with_scores:
                retrieved_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })
                
                # Build knowledge summary
                source = doc.metadata.get("source", "Unknown")
                knowledge_parts.append(f"[{source}] {doc.page_content}")
            
            local_knowledge = "\n\n".join(knowledge_parts)
            
            logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
            
            return {
                "retrieved_docs": retrieved_docs,
                "local_knowledge": local_knowledge,
                "messages": [AIMessage(content=f"Found {len(retrieved_docs)} relevant information sources.")],
                "next_agent": "itinerary",
                "should_continue": True,
            }
            
        except Exception as e:
            logger.error(f"Knowledge agent error: {e}", exc_info=True)
            # Continue even if retrieval fails
            return {
                "retrieved_docs": [],
                "local_knowledge": "Using general knowledge about Assam.",
                "next_agent": "itinerary",
                "should_continue": True,
            }
    
    @staticmethod
    def _build_search_query(
        destination: str,
        interests: List[str],
        user_query: str
    ) -> str:
        """Build optimized search query for vector store."""
        query_parts = [destination]
        
        if interests:
            query_parts.extend(interests)
        
        # Add key terms from user query
        if user_query:
            query_parts.append(user_query)
        
        return " ".join(query_parts)
