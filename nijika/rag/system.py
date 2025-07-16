"""
RAG (Retrieval-Augmented Generation) system for the Nijika AI Agent Framework
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import hashlib
import numpy as np
from pathlib import Path


@dataclass
class Document:
    """A document in the RAG system"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[List[float]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    chunks: List[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    """Result of a retrieval operation"""
    documents: List[Document]
    scores: List[float]
    query: str
    total_results: int
    retrieval_time: float


class DocumentProcessor:
    """Process documents for RAG system"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logging.getLogger("nijika.rag.processor")
    
    def process_document(self, content: str, metadata: Dict[str, Any] = None) -> Document:
        """Process a document"""
        doc_id = hashlib.md5(content.encode()).hexdigest()
        
        # Chunk the document
        chunks = self._chunk_text(content)
        
        document = Document(
            id=doc_id,
            content=content,
            metadata=metadata or {},
            chunks=chunks,
            source=metadata.get("source") if metadata else None
        )
        
        return document
    
    def _chunk_text(self, text: str) -> List[str]:
        """Chunk text into smaller pieces"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
        
        return chunks
    
    def process_file(self, file_path: str) -> Document:
        """Process a file"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {
            "source": str(path),
            "filename": path.name,
            "extension": path.suffix,
            "size": len(content),
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
        }
        
        return self.process_document(content, metadata)


class VectorStore:
    """Simple in-memory vector store"""
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        self.logger = logging.getLogger("nijika.rag.vectorstore")
    
    def add_document(self, document: Document):
        """Add a document to the vector store"""
        self.documents[document.id] = document
        
        if document.embeddings:
            self.embeddings[document.id] = np.array(document.embeddings)
        
        self.logger.debug(f"Added document: {document.id}")
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID"""
        return self.documents.get(doc_id)
    
    def search_by_similarity(self, query_embedding: List[float], top_k: int = 5) -> List[tuple]:
        """Search for similar documents"""
        if not self.embeddings:
            return []
        
        query_vector = np.array(query_embedding)
        similarities = []
        
        for doc_id, doc_embedding in self.embeddings.items():
            # Calculate cosine similarity
            similarity = np.dot(query_vector, doc_embedding) / (
                np.linalg.norm(query_vector) * np.linalg.norm(doc_embedding)
            )
            similarities.append((doc_id, similarity))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def search_by_text(self, query: str, top_k: int = 5) -> List[tuple]:
        """Search for documents by text matching"""
        results = []
        query_lower = query.lower()
        
        for doc_id, document in self.documents.items():
            # Simple text matching score
            content_lower = document.content.lower()
            score = content_lower.count(query_lower) / len(content_lower.split())
            
            if score > 0:
                results.append((doc_id, score))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the vector store"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            if doc_id in self.embeddings:
                del self.embeddings[doc_id]
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_documents": len(self.documents),
            "embedded_documents": len(self.embeddings),
            "average_content_length": sum(len(doc.content) for doc in self.documents.values()) / len(self.documents) if self.documents else 0
        }


class RAGSystem:
    """
    Main RAG system orchestrator
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("nijika.rag.system")
        
        # Configuration
        self.chunk_size = self.config.get("chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunk_overlap", 100)
        self.top_k = self.config.get("top_k", 5)
        self.embedding_model = self.config.get("embedding_model", "text-embedding-ada-002")
        
        # Initialize components
        self.processor = DocumentProcessor(self.chunk_size, self.chunk_overlap)
        self.vector_store = VectorStore()
        
        # Initialize if documents path is provided
        documents_path = self.config.get("documents_path")
        if documents_path:
            asyncio.create_task(self._load_documents(documents_path))
    
    async def _load_documents(self, documents_path: str):
        """Load documents from a directory"""
        path = Path(documents_path)
        if not path.exists():
            self.logger.warning(f"Documents path not found: {documents_path}")
            return
        
        supported_extensions = {'.txt', '.md', '.json', '.py', '.js', '.html', '.css'}
        
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    document = self.processor.process_file(str(file_path))
                    await self.add_document(document)
                    self.logger.debug(f"Loaded document: {file_path}")
                except Exception as e:
                    self.logger.error(f"Failed to load document {file_path}: {str(e)}")
    
    async def add_document(self, document: Document):
        """Add a document to the RAG system"""
        # Generate embeddings if not present
        if not document.embeddings:
            document.embeddings = await self._generate_embeddings(document.content)
        
        # Add to vector store
        self.vector_store.add_document(document)
        
        self.logger.info(f"Added document to RAG system: {document.id}")
    
    async def add_text(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """Add text content to the RAG system"""
        document = self.processor.process_document(text, metadata)
        await self.add_document(document)
        return document.id
    
    async def add_file(self, file_path: str) -> str:
        """Add a file to the RAG system"""
        document = self.processor.process_file(file_path)
        await self.add_document(document)
        return document.id
    
    async def retrieve(self, query: str, top_k: int = None) -> RetrievalResult:
        """Retrieve relevant documents for a query"""
        start_time = datetime.now()
        top_k = top_k or self.top_k
        
        # Generate query embedding
        query_embedding = await self._generate_embeddings(query)
        
        # Search for similar documents
        if query_embedding:
            similar_docs = self.vector_store.search_by_similarity(query_embedding, top_k)
        else:
            # Fallback to text search
            similar_docs = self.vector_store.search_by_text(query, top_k)
        
        # Build result
        documents = []
        scores = []
        
        for doc_id, score in similar_docs:
            document = self.vector_store.get_document(doc_id)
            if document:
                documents.append(document)
                scores.append(score)
        
        retrieval_time = (datetime.now() - start_time).total_seconds()
        
        result = RetrievalResult(
            documents=documents,
            scores=scores,
            query=query,
            total_results=len(documents),
            retrieval_time=retrieval_time
        )
        
        self.logger.debug(f"Retrieved {len(documents)} documents for query: {query[:50]}...")
        return result
    
    async def _generate_embeddings(self, text: str) -> Optional[List[float]]:
        """Generate embeddings for text"""
        try:
            # This would integrate with actual embedding providers
            # For now, return mock embeddings
            import hashlib
            import random
            
            # Generate deterministic but pseudo-random embeddings
            hash_obj = hashlib.md5(text.encode())
            seed = int(hash_obj.hexdigest(), 16) % (2**32)
            random.seed(seed)
            
            # Generate 1536-dimensional embeddings (OpenAI ada-002 size)
            embeddings = [random.uniform(-1, 1) for _ in range(1536)]
            
            return embeddings
        
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {str(e)}")
            return None
    
    async def search(self, query: str, filters: Dict[str, Any] = None, top_k: int = None) -> List[Document]:
        """Search for documents with optional filters"""
        result = await self.retrieve(query, top_k)
        
        documents = result.documents
        
        # Apply filters if provided
        if filters:
            filtered_docs = []
            for doc in documents:
                match = True
                for key, value in filters.items():
                    if key not in doc.metadata or doc.metadata[key] != value:
                        match = False
                        break
                
                if match:
                    filtered_docs.append(doc)
            
            documents = filtered_docs
        
        return documents
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID"""
        return self.vector_store.get_document(doc_id)
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the RAG system"""
        return self.vector_store.remove_document(doc_id)
    
    def list_documents(self) -> List[str]:
        """List all document IDs"""
        return list(self.vector_store.documents.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        vector_stats = self.vector_store.get_stats()
        
        return {
            "total_documents": vector_stats["total_documents"],
            "embedded_documents": vector_stats["embedded_documents"],
            "average_content_length": vector_stats["average_content_length"],
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "top_k": self.top_k,
            "embedding_model": self.embedding_model
        }
    
    async def update_document(self, doc_id: str, content: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Update a document"""
        document = self.get_document(doc_id)
        if not document:
            return False
        
        # Update content if provided
        if content:
            document.content = content
            document.chunks = self.processor._chunk_text(content)
            document.embeddings = await self._generate_embeddings(content)
        
        # Update metadata if provided
        if metadata:
            document.metadata.update(metadata)
        
        # Update timestamp
        document.timestamp = datetime.now()
        
        # Re-add to vector store
        self.vector_store.add_document(document)
        
        self.logger.info(f"Updated document: {doc_id}")
        return True
    
    async def reindex(self):
        """Reindex all documents"""
        self.logger.info("Starting RAG system reindexing...")
        
        document_ids = list(self.vector_store.documents.keys())
        
        for doc_id in document_ids:
            document = self.vector_store.get_document(doc_id)
            if document:
                # Regenerate embeddings
                document.embeddings = await self._generate_embeddings(document.content)
                
                # Re-add to vector store
                self.vector_store.add_document(document)
        
        self.logger.info(f"Reindexed {len(document_ids)} documents")
    
    def clear(self):
        """Clear all documents from the RAG system"""
        self.vector_store.documents.clear()
        self.vector_store.embeddings.clear()
        self.logger.info("Cleared all documents from RAG system")
    
    async def get_context(self, query: str, max_tokens: int = 4000) -> str:
        """Get context for a query with token limit"""
        result = await self.retrieve(query)
        
        context_parts = []
        current_tokens = 0
        
        for document in result.documents:
            # Rough token estimation (4 characters per token)
            doc_tokens = len(document.content) // 4
            
            if current_tokens + doc_tokens > max_tokens:
                break
            
            context_parts.append(f"Document: {document.metadata.get('source', 'Unknown')}")
            context_parts.append(document.content)
            context_parts.append("---")
            
            current_tokens += doc_tokens
        
        return "\n".join(context_parts)
    
    def export_documents(self, file_path: str):
        """Export all documents to a JSON file"""
        documents_data = []
        
        for document in self.vector_store.documents.values():
            doc_data = {
                "id": document.id,
                "content": document.content,
                "metadata": document.metadata,
                "timestamp": document.timestamp.isoformat(),
                "source": document.source,
                "chunks": document.chunks
            }
            documents_data.append(doc_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(documents_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Exported {len(documents_data)} documents to {file_path}")
    
    async def import_documents(self, file_path: str):
        """Import documents from a JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            documents_data = json.load(f)
        
        for doc_data in documents_data:
            document = Document(
                id=doc_data["id"],
                content=doc_data["content"],
                metadata=doc_data["metadata"],
                timestamp=datetime.fromisoformat(doc_data["timestamp"]),
                source=doc_data.get("source"),
                chunks=doc_data.get("chunks", [])
            )
            
            await self.add_document(document)
        
        self.logger.info(f"Imported {len(documents_data)} documents from {file_path}") 