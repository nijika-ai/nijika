"""
Memory management for the Nijika AI Agent Framework
"""

import asyncio
import logging
import json
import sqlite3
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import aiosqlite
from abc import ABC, abstractmethod

def make_serializable(obj, visited=None):
    """
    Convert complex objects to JSON serializable format
    """
    if visited is None:
        visited = set()
    
    # Handle circular references
    obj_id = id(obj)
    if obj_id in visited:
        return f"<circular reference to {type(obj).__name__}>"
    
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        visited.add(obj_id)
        result = {key: make_serializable(value, visited) for key, value in obj.items()}
        visited.remove(obj_id)
        return result
    elif isinstance(obj, (list, tuple)):
        visited.add(obj_id)
        result = [make_serializable(item, visited) for item in obj]
        visited.remove(obj_id)
        return result
    elif hasattr(obj, '__dict__'):
        # For objects with __dict__, convert to dict
        visited.add(obj_id)
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):  # Skip private attributes
                try:
                    result[key] = make_serializable(value, visited)
                except:
                    result[key] = f"<error serializing {key}>"
        visited.remove(obj_id)
        return result
    elif hasattr(obj, '_asdict'):
        # For namedtuples
        visited.add(obj_id)
        result = make_serializable(obj._asdict(), visited)
        visited.remove(obj_id)
        return result
    else:
        # For other types, try to convert to string
        try:
            return str(obj)
        except:
            return f"<{type(obj).__name__} object>"


class MemoryType(Enum):
    """Types of memory storage"""
    CONVERSATION = "conversation"
    EXECUTION = "execution"
    KNOWLEDGE = "knowledge"
    CONTEXT = "context"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryScope(Enum):
    """Memory scope levels"""
    SESSION = "session"
    AGENT = "agent"
    GLOBAL = "global"


@dataclass
class MemoryEntry:
    """A single memory entry"""
    id: str
    memory_type: MemoryType
    scope: MemoryScope
    agent_id: Optional[str]
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    ttl: Optional[datetime] = None
    importance: float = 0.5
    tags: List[str] = None


class BaseMemoryBackend(ABC):
    """Abstract base class for memory backends"""
    
    @abstractmethod
    async def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry"""
        pass
    
    @abstractmethod
    async def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID"""
        pass
    
    @abstractmethod
    async def search(self, query: str, memory_type: MemoryType = None, 
                    scope: MemoryScope = None, limit: int = 10) -> List[MemoryEntry]:
        """Search memory entries"""
        pass
    
    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        """Delete a memory entry"""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired entries"""
        pass


class SQLiteMemoryBackend(BaseMemoryBackend):
    """SQLite-based memory backend"""
    
    def __init__(self, db_path: str = "nijika_memory.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("nijika.memory.sqlite")
    
    async def initialize(self):
        """Initialize the database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    agent_id TEXT,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    ttl TEXT,
                    importance REAL DEFAULT 0.5,
                    tags TEXT
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_scope ON memory_entries(scope)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_id ON memory_entries(agent_id)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_entries(timestamp)
            """)
            
            await db.commit()
    
    async def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO memory_entries 
                (id, memory_type, scope, agent_id, content, metadata, timestamp, ttl, importance, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id,
                entry.memory_type.value,
                entry.scope.value,
                entry.agent_id,
                json.dumps(entry.content),
                json.dumps(entry.metadata),
                entry.timestamp.isoformat(),
                entry.ttl.isoformat() if entry.ttl else None,
                entry.importance,
                json.dumps(entry.tags) if entry.tags else None
            ))
            await db.commit()
        
        return entry.id
    
    async def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM memory_entries WHERE id = ?
            """, (entry_id,)) as cursor:
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return self._row_to_entry(row)
    
    async def search(self, query: str, memory_type: MemoryType = None, 
                    scope: MemoryScope = None, limit: int = 10) -> List[MemoryEntry]:
        """Search memory entries"""
        where_clauses = []
        params = []
        
        if memory_type:
            where_clauses.append("memory_type = ?")
            params.append(memory_type.value)
        
        if scope:
            where_clauses.append("scope = ?")
            params.append(scope.value)
        
        if query:
            where_clauses.append("(content LIKE ? OR metadata LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(f"""
                SELECT * FROM memory_entries 
                WHERE {where_clause}
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            """, params + [limit]) as cursor:
                rows = await cursor.fetchall()
                
                return [self._row_to_entry(row) for row in rows]
    
    async def delete(self, entry_id: str) -> bool:
        """Delete a memory entry"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM memory_entries WHERE id = ?", (entry_id,))
            await db.commit()
            return True
    
    async def cleanup_expired(self) -> int:
        """Clean up expired entries"""
        now = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                DELETE FROM memory_entries WHERE ttl IS NOT NULL AND ttl < ?
            """, (now,)) as cursor:
                count = cursor.rowcount
            
            await db.commit()
            return count
    
    def _row_to_entry(self, row) -> MemoryEntry:
        """Convert database row to MemoryEntry"""
        return MemoryEntry(
            id=row[0],
            memory_type=MemoryType(row[1]),
            scope=MemoryScope(row[2]),
            agent_id=row[3],
            content=json.loads(row[4]),
            metadata=json.loads(row[5]),
            timestamp=datetime.fromisoformat(row[6]),
            ttl=datetime.fromisoformat(row[7]) if row[7] else None,
            importance=row[8],
            tags=json.loads(row[9]) if row[9] else None
        )


class MemoryManager:
    """
    Main memory management system
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("nijika.memory")
        
        # Initialize backend
        backend_type = self.config.get("backend", "sqlite")
        if backend_type == "sqlite":
            self.backend = SQLiteMemoryBackend(
                self.config.get("db_path", "nijika_memory.db")
            )
        else:
            raise ValueError(f"Unsupported memory backend: {backend_type}")
        
        # Configuration
        self.max_entries = self.config.get("max_entries", 10000)
        self.cleanup_interval = self.config.get("cleanup_interval", 3600)  # 1 hour
        self.default_ttl = self.config.get("default_ttl", 86400)  # 24 hours
        
        # Initialize
        asyncio.create_task(self._initialize())
    
    async def _initialize(self):
        """Initialize the memory manager"""
        await self.backend.initialize()
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_task())
    
    async def _cleanup_task(self):
        """Periodic cleanup of expired entries"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                cleaned_count = await self.backend.cleanup_expired()
                if cleaned_count > 0:
                    self.logger.info(f"Cleaned up {cleaned_count} expired memory entries")
            except Exception as e:
                self.logger.error(f"Memory cleanup failed: {str(e)}")
    
    async def store_conversation(self, agent_id: str, query: str, response: str, 
                               context: Dict[str, Any] = None) -> str:
        """Store a conversation entry"""
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            memory_type=MemoryType.CONVERSATION,
            scope=MemoryScope.AGENT,
            agent_id=agent_id,
            content={
                "query": query,
                "response": response,
                "context": context or {}
            },
            metadata={
                "query_length": len(query),
                "response_length": len(response),
                "conversation_id": context.get("conversation_id") if context else None
            },
            timestamp=datetime.now(),
            ttl=datetime.now() + timedelta(seconds=self.default_ttl),
            importance=0.7
        )
        
        return await self.backend.store(entry)
    
    async def store_execution(self, execution_id: str, exec_context: Dict[str, Any], 
                            result: Dict[str, Any]) -> str:
        """Store an execution entry"""
        # Make context and result serializable
        serializable_context = make_serializable(exec_context)
        serializable_result = make_serializable(result)
        
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            memory_type=MemoryType.EXECUTION,
            scope=MemoryScope.AGENT,
            agent_id=exec_context.get("agent_id"),
            content={
                "execution_id": execution_id,
                "query": exec_context.get("query"),
                "result": serializable_result,
                "context": serializable_context
            },
            metadata={
                "execution_time": result.get("execution_time", 0),
                "status": result.get("status", "unknown"),
                "steps_count": len(result.get("results", []))
            },
            timestamp=datetime.now(),
            ttl=datetime.now() + timedelta(seconds=self.default_ttl * 7),  # Keep longer
            importance=0.8
        )
        
        return await self.backend.store(entry)
    
    async def store_knowledge(self, agent_id: str, knowledge: Dict[str, Any], 
                            tags: List[str] = None) -> str:
        """Store a knowledge entry"""
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            memory_type=MemoryType.KNOWLEDGE,
            scope=MemoryScope.AGENT,
            agent_id=agent_id,
            content=knowledge,
            metadata={
                "source": knowledge.get("source", "unknown"),
                "confidence": knowledge.get("confidence", 0.5)
            },
            timestamp=datetime.now(),
            ttl=None,  # Knowledge doesn't expire
            importance=0.9,
            tags=tags or []
        )
        
        return await self.backend.store(entry)
    
    async def get_conversation_history(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for an agent"""
        entries = await self.backend.search(
            query="",
            memory_type=MemoryType.CONVERSATION,
            scope=MemoryScope.AGENT,
            limit=limit
        )
        
        # Filter by agent_id and format
        conversations = []
        for entry in entries:
            if entry.agent_id == agent_id:
                conversations.append({
                    "id": entry.id,
                    "query": entry.content["query"],
                    "response": entry.content["response"],
                    "timestamp": entry.timestamp.isoformat(),
                    "context": entry.content.get("context", {})
                })
        
        return conversations
    
    async def get_execution_history(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get execution history for an agent"""
        entries = await self.backend.search(
            query="",
            memory_type=MemoryType.EXECUTION,
            scope=MemoryScope.AGENT,
            limit=limit
        )
        
        # Filter by agent_id and format
        executions = []
        for entry in entries:
            if entry.agent_id == agent_id:
                executions.append({
                    "id": entry.id,
                    "execution_id": entry.content["execution_id"],
                    "query": entry.content["query"],
                    "result": entry.content["result"],
                    "timestamp": entry.timestamp.isoformat()
                })
        
        return executions
    
    async def search_knowledge(self, query: str, agent_id: str = None, 
                             tags: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge entries"""
        entries = await self.backend.search(
            query=query,
            memory_type=MemoryType.KNOWLEDGE,
            limit=limit
        )
        
        # Filter and format
        knowledge_entries = []
        for entry in entries:
            if agent_id and entry.agent_id != agent_id:
                continue
            
            if tags and not any(tag in (entry.tags or []) for tag in tags):
                continue
            
            knowledge_entries.append({
                "id": entry.id,
                "content": entry.content,
                "tags": entry.tags,
                "importance": entry.importance,
                "timestamp": entry.timestamp.isoformat()
            })
        
        return knowledge_entries
    
    async def get_context(self, agent_id: str, query: str) -> Dict[str, Any]:
        """Get relevant context for a query"""
        # Search recent conversations
        conversations = await self.get_conversation_history(agent_id, limit=5)
        
        # Search relevant knowledge
        knowledge = await self.search_knowledge(query, agent_id, limit=5)
        
        # Search recent executions
        executions = await self.get_execution_history(agent_id, limit=3)
        
        return {
            "conversations": conversations,
            "knowledge": knowledge,
            "executions": executions,
            "timestamp": datetime.now().isoformat()
        }
    
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a memory entry"""
        return await self.backend.delete(entry_id)
    
    async def clear_agent_memory(self, agent_id: str) -> int:
        """Clear all memory for an agent"""
        # This would require a more sophisticated implementation
        # For now, we'll just note it's not implemented
        raise NotImplementedError("Agent memory clearing not implemented")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        # This would require backend-specific implementation
        return {
            "backend_type": type(self.backend).__name__,
            "max_entries": self.max_entries,
            "cleanup_interval": self.cleanup_interval,
            "default_ttl": self.default_ttl
        } 