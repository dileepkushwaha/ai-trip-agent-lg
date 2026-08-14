"""
Embedding management for RAG system.
Supports multiple embedding providers (OpenAI, HuggingFace).
"""

import logging
from typing import List

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Manages text embeddings with multi-provider support.
    """
    
    def __init__(self, settings):
        """
        Initialize embedding manager.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.provider = settings.embedding_provider.lower()
        self._embeddings = None
        
        logger.info(f"Initializing EmbeddingManager with provider: {self.provider}")
    
    def get_embeddings(self) -> Embeddings:
        """
        Get embeddings instance based on configured provider.
        
        Returns:
            Embeddings instance
        """
        if self._embeddings is not None:
            return self._embeddings
        
        try:
            if self.provider == "openai":
                self._embeddings = self._init_openai_embeddings()
            elif self.provider == "huggingface":
                self._embeddings = self._init_huggingface_embeddings()
            else:
                logger.warning(f"Unknown provider {self.provider}, falling back to HuggingFace")
                self._embeddings = self._init_huggingface_embeddings()
            
            logger.info(f"✅ Embeddings initialized: {self.provider}")
            return self._embeddings
            
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def _init_openai_embeddings(self) -> Embeddings:
        """Initialize OpenAI embeddings."""
        if not self.settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        return OpenAIEmbeddings(
            model=self.settings.embedding_model,
            openai_api_key=self.settings.openai_api_key,
        )
    
    def _init_huggingface_embeddings(self) -> Embeddings:
        """Initialize HuggingFace embeddings."""
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except ImportError:
            # Fallback to old import if new package not available
            logger.warning("langchain-huggingface not found, using legacy import")
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            texts: List of text documents
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.get_embeddings()
        return embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query.
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        embeddings = self.get_embeddings()
        return embeddings.embed_query(text)
