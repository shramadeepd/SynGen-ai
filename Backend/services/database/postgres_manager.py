"""
PostgreSQL Database Manager for SynGen AI
Handles connections and operations with PostgreSQL database
"""

import asyncio
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
from typing import Dict, List, Any, Optional
import json
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class PostgreSQLManager:
    """PostgreSQL database manager with async support"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv(
            "DATABASE_URL", 
            "postgresql://syngen_user:syngen_password@localhost:5432/syngen_ai"
        )
        self._pool = None
        
    async def initialize_pool(self, min_size: int = 5, max_size: int = 20):
        """Initialize connection pool"""
        try:
            self._pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=min_size,
                max_size=max_size,
                command_timeout=30
            )
            logger.info("PostgreSQL connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise
    
    async def close_pool(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
            logger.info("PostgreSQL connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get async database connection from pool"""
        if not self._pool:
            await self.initialize_pool()
        
        async with self._pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        async with self.get_connection() as conn:
            try:
                if params:
                    rows = await conn.fetch(query, *params)
                else:
                    rows = await conn.fetch(query)
                
                return [dict(row) for row in rows]
                
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                raise
    
    async def execute_query_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute SELECT query and return single result"""
        async with self.get_connection() as conn:
            try:
                if params:
                    row = await conn.fetchrow(query, *params)
                else:
                    row = await conn.fetchrow(query)
                
                return dict(row) if row else None
                
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise
    
    async def execute_command(self, command: str, params: tuple = None) -> str:
        """Execute INSERT/UPDATE/DELETE command"""
        async with self.get_connection() as conn:
            try:
                if params:
                    result = await conn.execute(command, *params)
                else:
                    result = await conn.execute(command)
                
                return result
                
            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                raise
    
    def get_sync_connection(self):
        """Get synchronous connection for non-async operations"""
        return psycopg2.connect(
            self.connection_string,
            cursor_factory=RealDictCursor
        )
    
    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get table schema information"""
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = $1 
        ORDER BY ordinal_position
        """
        
        columns = await self.execute_query(query, (table_name,))
        
        # Get sample data
        sample_query = f"SELECT * FROM {table_name} LIMIT 3"
        sample_data = await self.execute_query(sample_query)
        
        return {
            "table": table_name,
            "columns": columns,
            "sample_data": sample_data
        }
    
    async def get_database_schema(self) -> Dict[str, Any]:
        """Get complete database schema"""
        # Get all table names
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        
        tables = await self.execute_query(tables_query)
        table_names = [table['table_name'] for table in tables]
        
        schema = {}
        for table_name in table_names:
            schema[table_name] = await self.get_table_info(table_name)
        
        return schema
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

class MongoDBManager:
    """MongoDB manager for document storage"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or "mongodb://localhost:27017/syngen_documents"
        self._client = None
        self._db = None
        self._collection = None
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            from pymongo import MongoClient
            self._client = MongoClient(self.connection_string)
            self._db = self._client.get_default_database()
            self._collection = self._db.policy_documents
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search documents using text search"""
        if self._collection is None:
            self.connect()
        
        try:
            # Use text search with MongoDB
            search_results = self._collection.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(top_k)
            
            documents = []
            for doc in search_results:
                documents.append({
                    "id": doc.get("id", str(doc.get("_id"))),
                    "title": doc.get("title", ""),
                    "content": doc.get("content", ""),
                    "relevance_score": doc.get("score", 0)
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total document count"""
        if self._collection is None:
            self.connect()
        
        try:
            return self._collection.count_documents({})
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")

# Global instances
postgres_manager = PostgreSQLManager()
mongodb_manager = MongoDBManager()

# Async context manager for database operations
@asynccontextmanager
async def get_db_connection():
    """Get database connection context manager"""
    try:
        yield postgres_manager
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        raise

# Convenience functions
async def execute_sql_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute SQL query and return results"""
    return await postgres_manager.execute_query(query, params)

async def get_schema_info() -> str:
    """Get database schema as JSON string"""
    schema = await postgres_manager.get_database_schema()
    return json.dumps(schema, indent=2, default=str)

async def search_policy_documents(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search policy documents in MongoDB"""
    return mongodb_manager.search_documents(query, top_k)