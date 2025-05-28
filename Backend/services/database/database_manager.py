"""
Dual Database Manager for SynGen AI
Manages both PostgreSQL (structured data) and MongoDB (documents) databases

Architecture:
- PostgreSQL: Supply chain transactional data for Text-to-SQL queries
- MongoDB: Policy documents and unstructured data for RAG
- Unified interface for both databases
"""
import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json

# PostgreSQL imports
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# MongoDB imports
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from bson import ObjectId

# Local imports
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Configuration for database connections"""
    # PostgreSQL config
    postgres_url: str
    # MongoDB config
    mongodb_url: str
    
    # Optional fields with defaults
    postgres_max_connections: int = 10
    mongodb_database: str = "syngen_documents"
    connection_timeout: int = 30
    query_timeout: int = 60

class PostgreSQLManager:
    """Manages PostgreSQL connections and operations"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool = None
        self._engine = None
        self._session_factory = None
        
    async def initialize(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self._pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=2,
                max_size=self.config.postgres_max_connections,
                command_timeout=self.config.query_timeout
            )
            
            # Also create SQLAlchemy engine for ORM operations
            self._engine = create_engine(self.config.postgres_url, echo=False)
            self._session_factory = sessionmaker(bind=self._engine)
            
            logger.info("PostgreSQL connection pool initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            return False
    
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self._pool:
            await self.initialize()
        return await self._pool.acquire()
    
    async def release_connection(self, conn):
        """Release connection back to pool"""
        if self._pool and conn:
            await self._pool.release(conn)
    
    async def execute_query(self, query: str, params: List = None) -> List[Dict]:
        """Execute a SQL query and return results"""
        conn = None
        try:
            conn = await self.get_connection()
            
            if params:
                rows = await conn.fetch(query, *params)
            else:
                rows = await conn.fetch(query)
            
            # Convert to list of dictionaries
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if conn:
                await self.release_connection(conn)
    
    async def execute_scalar(self, query: str, params: List = None) -> Any:
        """Execute query and return single value"""
        conn = None
        try:
            conn = await self.get_connection()
            
            if params:
                result = await conn.fetchval(query, *params)
            else:
                result = await conn.fetchval(query)
            
            return result
            
        except Exception as e:
            logger.error(f"Scalar query execution failed: {e}")
            raise
        finally:
            if conn:
                await self.release_connection(conn)
    
    def get_session(self):
        """Get SQLAlchemy session for ORM operations"""
        if not self._session_factory:
            raise RuntimeError("PostgreSQL not initialized")
        return self._session_factory()
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information"""
        schema_query = """
        SELECT 
            t.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_schema = 'public' 
        AND t.table_type = 'BASE TABLE'
        ORDER BY t.table_name, c.ordinal_position
        """
        
        rows = await self.execute_query(schema_query)
        
        # Group by table
        tables = {}
        for row in rows:
            table_name = row['table_name']
            if table_name not in tables:
                tables[table_name] = {'columns': []}
            
            tables[table_name]['columns'].append({
                'name': row['column_name'],
                'type': row['data_type'],
                'nullable': row['is_nullable'] == 'YES',
                'default': row['column_default']
            })
        
        return {'tables': tables}
    
    async def get_table_sample(self, table_name: str, limit: int = 5) -> List[Dict]:
        """Get sample rows from a table"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return await self.execute_query(query)
    
    async def close(self):
        """Close database connections"""
        if self._pool:
            await self._pool.close()

class MongoDBManager:
    """Manages MongoDB connections and operations"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._client = None
        self._database = None
        
    async def initialize(self):
        """Initialize MongoDB connection"""
        try:
            self._client = AsyncIOMotorClient(
                self.config.mongodb_url,
                serverSelectionTimeoutMS=self.config.connection_timeout * 1000
            )
            
            # Test connection
            await self._client.admin.command('ping')
            
            self._database = self._client[self.config.mongodb_database]
            
            logger.info("MongoDB connection initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {e}")
            return False
    
    async def get_database(self):
        """Get database instance"""
        if not self._database:
            await self.initialize()
        return self._database
    
    async def insert_document(self, collection: str, document: Dict) -> str:
        """Insert a document and return its ID"""
        try:
            db = await self.get_database()
            result = await db[collection].insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert document: {e}")
            raise
    
    async def insert_many_documents(self, collection: str, documents: List[Dict]) -> List[str]:
        """Insert multiple documents"""
        try:
            db = await self.get_database()
            result = await db[collection].insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Failed to insert documents: {e}")
            raise
    
    async def find_documents(self, collection: str, query: Dict = None, 
                           limit: int = None, skip: int = 0) -> List[Dict]:
        """Find documents in collection"""
        try:
            db = await self.get_database()
            cursor = db[collection].find(query or {})
            
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            documents = await cursor.to_list(length=None)
            
            # Convert ObjectId to string
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to find documents: {e}")
            raise
    
    async def find_one_document(self, collection: str, query: Dict) -> Optional[Dict]:
        """Find single document"""
        try:
            db = await self.get_database()
            document = await db[collection].find_one(query)
            
            if document and '_id' in document:
                document['_id'] = str(document['_id'])
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to find document: {e}")
            raise
    
    async def update_document(self, collection: str, query: Dict, update: Dict) -> bool:
        """Update a document"""
        try:
            db = await self.get_database()
            result = await db[collection].update_one(query, {"$set": update})
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            raise
    
    async def delete_document(self, collection: str, query: Dict) -> bool:
        """Delete a document"""
        try:
            db = await self.get_database()
            result = await db[collection].delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise
    
    async def create_text_index(self, collection: str, fields: List[str]):
        """Create text index for search"""
        try:
            db = await self.get_database()
            index_spec = [(field, "text") for field in fields]
            await db[collection].create_index(index_spec)
            logger.info(f"Text index created on {collection} for fields: {fields}")
        except Exception as e:
            logger.error(f"Failed to create text index: {e}")
            raise
    
    async def text_search(self, collection: str, search_text: str, 
                         limit: int = 10) -> List[Dict]:
        """Perform text search"""
        try:
            db = await self.get_database()
            cursor = db[collection].find(
                {"$text": {"$search": search_text}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            documents = await cursor.to_list(length=None)
            
            # Convert ObjectId to string
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return documents
            
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            raise
    
    async def get_collection_stats(self, collection: str) -> Dict:
        """Get collection statistics"""
        try:
            db = await self.get_database()
            stats = await db.command("collStats", collection)
            return {
                'count': stats.get('count', 0),
                'size': stats.get('size', 0),
                'avgObjSize': stats.get('avgObjSize', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'count': 0, 'size': 0, 'avgObjSize': 0}
    
    async def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()

class DualDatabaseManager:
    """Unified manager for both PostgreSQL and MongoDB"""
    
    def __init__(self, 
                 postgres_url: str = None,
                 mongodb_url: str = None,
                 mongodb_database: str = "syngen_documents"):
        
        # Use environment variables as defaults
        postgres_url = postgres_url or os.getenv(
            "DATABASE_URL", 
            "postgresql://syngen_user:syngen_password@localhost:5432/syngen_ai"
        )
        mongodb_url = mongodb_url or os.getenv(
            "MONGODB_URL", 
            "mongodb://localhost:27017"
        )
        
        self.config = DatabaseConfig(
            postgres_url=postgres_url,
            mongodb_url=mongodb_url,
            mongodb_database=mongodb_database
        )
        
        self.postgres = PostgreSQLManager(self.config)
        self.mongodb = MongoDBManager(self.config)
        
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize both databases"""
        if self._initialized:
            return True
        
        postgres_ok = await self.postgres.initialize()
        mongodb_ok = await self.mongodb.initialize()
        
        if postgres_ok and mongodb_ok:
            self._initialized = True
            logger.info("Dual database manager initialized successfully")
            
            # Create text indexes for document search
            await self._setup_mongodb_indexes()
            
            return True
        else:
            logger.error("Failed to initialize one or both databases")
            return False
    
    async def _setup_mongodb_indexes(self):
        """Setup MongoDB indexes for efficient searching"""
        try:
            # Create text index on policy documents
            await self.mongodb.create_text_index(
                "policy_documents", 
                ["title", "content", "filename"]
            )
            
            # Create index on chat history
            await self.mongodb.create_text_index(
                "chat_history",
                ["query", "response"]
            )
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create MongoDB indexes: {e}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get health status of both databases"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "postgres": {"status": "down", "details": {}},
            "mongodb": {"status": "down", "details": {}},
            "overall": "down"
        }
        
        # Test PostgreSQL
        try:
            result = await self.postgres.execute_scalar("SELECT 1")
            if result == 1:
                health["postgres"]["status"] = "up"
                
                # Get table counts
                tables_query = """
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins + n_tup_upd + n_tup_del as total_operations
                FROM pg_stat_user_tables
                ORDER BY total_operations DESC
                LIMIT 5
                """
                tables = await self.postgres.execute_query(tables_query)
                health["postgres"]["details"] = {"top_tables": tables}
                
        except Exception as e:
            health["postgres"]["details"] = {"error": str(e)}
        
        # Test MongoDB
        try:
            db = await self.mongodb.get_database()
            collections = await db.list_collection_names()
            
            health["mongodb"]["status"] = "up"
            health["mongodb"]["details"] = {
                "collections": collections,
                "collection_count": len(collections)
            }
            
            # Get collection stats
            for collection in collections[:3]:  # Limit to first 3
                stats = await self.mongodb.get_collection_stats(collection)
                health["mongodb"]["details"][f"{collection}_stats"] = stats
                
        except Exception as e:
            health["mongodb"]["details"] = {"error": str(e)}
        
        # Overall status
        if (health["postgres"]["status"] == "up" and 
            health["mongodb"]["status"] == "up"):
            health["overall"] = "up"
        elif (health["postgres"]["status"] == "up" or 
              health["mongodb"]["status"] == "up"):
            health["overall"] = "partial"
        
        return health
    
    # PostgreSQL convenience methods
    async def execute_sql(self, query: str, params: List = None) -> List[Dict]:
        """Execute SQL query on PostgreSQL"""
        return await self.postgres.execute_query(query, params)
    
    async def get_sql_schema(self) -> Dict[str, Any]:
        """Get PostgreSQL schema information"""
        return await self.postgres.get_schema_info()
    
    async def get_table_sample(self, table_name: str, limit: int = 5) -> List[Dict]:
        """Get sample data from PostgreSQL table"""
        return await self.postgres.get_table_sample(table_name, limit)
    
    # MongoDB convenience methods
    async def store_document(self, collection: str, document: Dict) -> str:
        """Store document in MongoDB"""
        # Add timestamp
        document['created_at'] = datetime.now()
        return await self.mongodb.insert_document(collection, document)
    
    async def search_documents(self, collection: str, search_text: str, 
                             limit: int = 10) -> List[Dict]:
        """Search documents in MongoDB"""
        return await self.mongodb.text_search(collection, search_text, limit)
    
    async def get_documents(self, collection: str, query: Dict = None, 
                          limit: int = None) -> List[Dict]:
        """Get documents from MongoDB"""
        return await self.mongodb.find_documents(collection, query, limit)
    
    # Combined operations
    async def store_query_log(self, user_id: str, query: str, 
                            sql_query: str = None, results: List[Dict] = None,
                            response: str = None, metadata: Dict = None):
        """Store query log in MongoDB for analytics"""
        log_entry = {
            "user_id": user_id,
            "query": query,
            "sql_query": sql_query,
            "results_count": len(results) if results else 0,
            "response": response,
            "metadata": metadata or {},
            "timestamp": datetime.now(),
            "session_id": metadata.get("session_id") if metadata else None
        }
        
        return await self.store_document("query_logs", log_entry)
    
    async def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's query history from MongoDB"""
        query = {"user_id": user_id}
        history = await self.mongodb.find_documents(
            "query_logs", 
            query, 
            limit=limit
        )
        
        # Sort by timestamp descending
        return sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    async def close(self):
        """Close all database connections"""
        await self.postgres.close()
        await self.mongodb.close()
        self._initialized = False
        logger.info("All database connections closed")

# Global instance
_db_manager = None

async def get_database_manager() -> DualDatabaseManager:
    """Get the global database manager instance"""
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DualDatabaseManager()
        await _db_manager.initialize()
    
    return _db_manager

async def close_database_connections():
    """Close all database connections"""
    global _db_manager
    if _db_manager:
        await _db_manager.close()
        _db_manager = None

# Context manager for database operations
class DatabaseContext:
    """Context manager for database operations"""
    
    def __init__(self):
        self.db_manager = None
    
    async def __aenter__(self) -> DualDatabaseManager:
        self.db_manager = await get_database_manager()
        return self.db_manager
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't close here, let the global manager handle it
        pass

# Convenience function
async def with_database():
    """Get database context manager"""
    return DatabaseContext()

if __name__ == "__main__":
    async def test_connections():
        """Test both database connections"""
        db_manager = DualDatabaseManager()
        
        if await db_manager.initialize():
            print("✅ Both databases initialized successfully")
            
            # Test PostgreSQL
            try:
                result = await db_manager.execute_sql("SELECT 1 as test")
                print(f"✅ PostgreSQL test: {result}")
            except Exception as e:
                print(f"❌ PostgreSQL test failed: {e}")
            
            # Test MongoDB
            try:
                doc_id = await db_manager.store_document("test", {"message": "Hello MongoDB"})
                print(f"✅ MongoDB test: Document stored with ID {doc_id}")
            except Exception as e:
                print(f"❌ MongoDB test failed: {e}")
            
            # Get health status
            health = await db_manager.get_system_health()
            print(f"📊 System Health: {health['overall']}")
            
            await db_manager.close()
        else:
            print("❌ Failed to initialize databases")
    
    asyncio.run(test_connections())