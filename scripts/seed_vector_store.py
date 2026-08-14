"""
Script to seed the vector database with Assam travel knowledge.
Loads markdown files and creates embeddings in ChromaDB.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_core.documents import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader

from config import get_settings
from services.rag.embeddings import EmbeddingManager
from services.rag.vector_store import VectorStoreManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_documents(data_dir: str) -> list[Document]:
    """
    Load documents from directory.
    
    Args:
        data_dir: Directory containing markdown files
        
    Returns:
        List of loaded documents
    """
    logger.info(f"Loading documents from: {data_dir}")
    
    try:
        # Load markdown files
        loader = DirectoryLoader(
            data_dir,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} documents")
        
        # Add metadata
        for doc in documents:
            # Extract filename as source
            source = Path(doc.metadata.get("source", "")).stem
            doc.metadata["source"] = source
            doc.metadata["type"] = "travel_guide"
        
        return documents
        
    except Exception as e:
        logger.error(f"Failed to load documents: {e}")
        raise


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[Document]:
    """
    Split documents into chunks.
    
    Args:
        documents: List of documents to chunk
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of chunked documents
    """
    logger.info(f"Chunking {len(documents)} documents...")
    
    text_splitter = VectorStoreManager.create_text_splitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    chunked_docs = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunked_docs)} chunks")
    
    return chunked_docs


def seed_vector_store(
    data_dir: str,
    reset: bool = False,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    """
    Seed vector store with travel knowledge.
    
    Args:
        data_dir: Directory containing data files
        reset: Whether to reset the collection first
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    """
    try:
        # Initialize components
        logger.info("Initializing components...")
        settings = get_settings()
        embedding_manager = EmbeddingManager(settings)
        vector_store_manager = VectorStoreManager(settings, embedding_manager)
        
        # Reset collection if requested
        if reset:
            logger.warning("Resetting vector store collection...")
            try:
                vector_store_manager.delete_collection()
                logger.info("Collection deleted")
            except Exception as e:
                logger.warning(f"Could not delete collection: {e}")
        
        # Load documents
        documents = load_documents(data_dir)
        
        if not documents:
            logger.warning("No documents found to seed")
            return
        
        # Chunk documents
        chunked_docs = chunk_documents(
            documents,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Add to vector store
        logger.info("Adding documents to vector store...")
        ids = vector_store_manager.add_documents(chunked_docs, batch_size=50)
        
        logger.info(f"✅ Successfully seeded {len(ids)} document chunks")
        
        # Show statistics
        stats = vector_store_manager.get_collection_stats()
        logger.info(f"Collection stats: {stats}")
        
        # Test retrieval
        logger.info("Testing retrieval...")
        test_query = "What can I see in Kaziranga?"
        results = vector_store_manager.similarity_search(test_query, k=3)
        
        logger.info(f"Test query: '{test_query}'")
        logger.info(f"Retrieved {len(results)} documents")
        
        if results:
            logger.info(f"Top result: {results[0].page_content[:200]}...")
        
        logger.info("✅ Seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        raise


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed vector database with travel knowledge")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/seed",
        help="Directory containing data files"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset collection before seeding"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Text chunk size"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Text chunk overlap"
    )
    
    args = parser.parse_args()
    
    # Resolve data directory path
    data_dir = Path(args.data_dir)
    if not data_dir.is_absolute():
        data_dir = project_root / data_dir
    
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)
    
    logger.info(f"Starting vector store seeding...")
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Reset: {args.reset}")
    logger.info(f"Chunk size: {args.chunk_size}")
    logger.info(f"Chunk overlap: {args.chunk_overlap}")
    
    seed_vector_store(
        data_dir=str(data_dir),
        reset=args.reset,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )


if __name__ == "__main__":
    main()
