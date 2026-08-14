"""
Vector store manager for ChromaDB integration.
Handles document storage, retrieval, and similarity search.
"""

import logging
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import Settings
from services.rag.embeddings import EmbeddingManager

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manager for ChromaDB vector store operations."""
    
    def __init__(self, settings: Settings, embedding_manager: EmbeddingManager):
        """Initialize vector store manager."""
        self.settings = settings
        self.embedding_manager = embedding_manager
        self._vector_store: Optional[Chroma] = None
        self._client: Optional[chromadb.HttpClient] = None
    
    def get_client(self) -> chromadb.HttpClient:
        """Get ChromaDB client."""
        if self._client is not None:
            return self._client
        
        try:
            self._client = chromadb.HttpClient(
                host=self.settings.chroma_host,
                port=self.settings.chroma_port,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"Connected to ChromaDB at {self.settings.get_chroma_url()}")
            return self._client
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    def get_vector_store(self) -> Chroma:
        """Get or create vector store instance."""
        if self._vector_store is not None:
            return self._vector_store
        
        try:
            client = self.get_client()
            embeddings = self.embedding_manager.get_embeddings()
            
            self._vector_store = Chroma(
                client=client,
                collection_name=self.settings.chroma_collection_name,
                embedding_function=embeddings,
            )
            
            logger.info(f"Vector store initialized with collection: {self.settings.chroma_collection_name}")
            return self._vector_store
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> List[str]:
        """
        Add documents to vector store in batches.
        
        Args:
            documents: List of documents to add
            batch_size: Number of documents to process at once
            
        Returns:
            List of document IDs
        """
        vector_store = self.get_vector_store()
        
        try:
            # Process in batches to avoid memory issues
            all_ids = []
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                ids = vector_store.add_documents(batch)
                all_ids.extend(ids)
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch)} documents")
            
            logger.info(f"Successfully added {len(all_ids)} documents to vector store")
            return all_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Metadata filter
            
        Returns:
            List of similar documents
        """
        vector_store = self.get_vector_store()
        k = k or self.settings.rag_top_k
        
        try:
            results = vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def similarity_search_with_score(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        vector_store = self.get_vector_store()
        k = k or self.settings.rag_top_k
        
        try:
            results = vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            
            # Filter by similarity threshold
            filtered_results = [
                (doc, score) for doc, score in results
                if score >= self.settings.rag_similarity_threshold
            ]
            
            logger.info(
                f"Found {len(filtered_results)} documents above threshold "
                f"(total: {len(results)})"
            )
            return filtered_results
            
        except Exception as e:
            logger.error(f"Similarity search with score failed: {e}")
            return []
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            client = self.get_client()
            client.delete_collection(self.settings.chroma_collection_name)
            self._vector_store = None
            logger.info(f"Deleted collection: {self.settings.chroma_collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            vector_store = self.get_vector_store()
            collection = vector_store._collection
            
            count = collection.count()
            
            return {
                "name": self.settings.chroma_collection_name,
                "count": count,
                "embedding_dimension": self.settings.embedding_dimension,
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    @staticmethod
    def create_text_splitter(
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> RecursiveCharacterTextSplitter:
        """Create text splitter for document chunking."""
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
