"""
Database connection and schema service module for the SynGen AI platform.

This module provides database connection utilities and a schema service for 
retrieving database metadata with efficient caching. It supports PostgreSQL 
connections and Redis-based caching.

The schema service automatically extracts table and column information along
with sample data to provide comprehensive context for LLM-based SQL generation.

Features:
- Asynchronous database connections using asyncpg
- Redis-based schema caching with TTL
- Comprehensive schema introspection including foreign keys and constraints
- Sample data extraction for better LLM context
"""
import os
import asyncpg
import asyncio
import json
import redis
import logging
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Configuration
DB_URL = os.getenv("DATABASE_URL", "postgresql://syngen_user:syngen_password@localhost:5432/syngen_ai")
WRITE_DB_URL = os.getenv("DATABASE_URL", DB_URL)  # Use same URL for both read and write
CACHE_TTL = int(os.getenv("SCHEMA_CACHE_TTL", "600"))  # Cache TTL in seconds (default: 10 minutes)
SAMPLE_ROWS = int(os.getenv("SCHEMA_SAMPLE_ROWS", "5"))  # Number of sample rows per table
MAX_TABLE_SIZE = int(os.getenv("SCHEMA_MAX_TABLE_SIZE", "1000000"))  # Skip sampling for huge tables
SCHEMA_VERSION = "v2"  # Increment when schema format changes

# Redis client for caching
redis_cli = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"), 
    decode_responses=True
)

# Logger setup
logger = logging.getLogger("syngen.db")

# Schema keys
SCHEMA_KEY = f"t2sql:schema:{SCHEMA_VERSION}"
TABLE_STATS_KEY = f"t2sql:table_stats:{SCHEMA_VERSION}"
RELATIONSHIPS_KEY = f"t2sql:relationships:{SCHEMA_VERSION}"

# Connection pools
_ro_pool = None  # Read-only connection pool
_rw_pool = None  # Read-write connection pool

async def init_db_pools():
    """Initialize database connection pools."""
    global _ro_pool, _rw_pool
    
    if _ro_pool is None:
        _ro_pool = await asyncpg.create_pool(
            DB_URL, 
            min_size=2,
            max_size=10
        )
        logger.info("Read-only database pool initialized")
    
    if _rw_pool is None and WRITE_DB_URL != DB_URL:
        _rw_pool = await asyncpg.create_pool(
            WRITE_DB_URL,
            min_size=1,
            max_size=5
        )
        logger.info("Read-write database pool initialized")


async def get_ro_conn():
    """Get a connection from the read-only pool."""
    global _ro_pool
    
    if _ro_pool is None:
        await init_db_pools()
    
    return await _ro_pool.acquire()


async def get_rw_conn():
    """Get a connection from the read-write pool."""
    global _rw_pool
    
    if _rw_pool is None:
        await init_db_pools()
    
    if _rw_pool:
        return await _rw_pool.acquire()
    else:
        # Fallback to read-only pool if no write pool is configured
        return await get_ro_conn()


async def get_conn():
    """Get a database connection (read-only by default for safety)."""
    return await get_ro_conn()


@asynccontextmanager
async def db_transaction():
    """Context manager for database transactions with automatic rollback on error."""
    async with (await get_rw_conn()).transaction() as txn:
        yield txn


class SchemaService:
    """
    Service for retrieving and caching database schema information.
    
    This service provides comprehensive database metadata including:
    - Table and column definitions
    - Primary and foreign keys
    - Constraints and indexes
    - Sample data for each table
    - Table statistics
    
    The schema information is cached in Redis with a configurable TTL.
    """
    
    def __init__(
        self,
        cache_ttl: int = CACHE_TTL,
        sample_rows: int = SAMPLE_ROWS,
        max_table_size: int = MAX_TABLE_SIZE
    ):
        """
        Initialize the schema service.
        
        Args:
            cache_ttl: Time-to-live for cached schema in seconds
            sample_rows: Number of sample rows to include per table
            max_table_size: Skip sampling for tables larger than this
        """
        self.cache_ttl = cache_ttl
        self.sample_rows = sample_rows
        self.max_table_size = max_table_size
        self.redis = redis_cli
        
    async def load_schema(self, force_refresh: bool = False) -> str:
        """
        Load database schema with caching.
        
        Args:
            force_refresh: Whether to force a refresh of the schema cache
            
        Returns:
            JSON string containing schema information
        """
        # Try to get from cache unless forced refresh
        if not force_refresh:
            cached = self.redis.get(SCHEMA_KEY)
            if cached:
                logger.debug("Schema loaded from cache")
                return cached
        
        logger.info("Refreshing schema cache")
        start_time = time.time()
        
        # Get schema, relationships, and table stats in parallel
        schema, relationships, table_stats = await asyncio.gather(
            self._fetch_schema(),
            self._fetch_relationships(),
            self._fetch_table_stats()
        )
        
        # Combine all schema information
        complete_schema = {
            "tables": schema,
            "relationships": relationships,
            "table_stats": table_stats,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "schema_version": SCHEMA_VERSION
            }
        }
        
        # Convert to JSON
        schema_json = json.dumps(complete_schema)
        
        # Cache in Redis
        self.redis.setex(SCHEMA_KEY, self.cache_ttl, schema_json)
        
        # Log performance
        elapsed = time.time() - start_time
        logger.info(f"Schema refreshed in {elapsed:.2f}s")
        
        return schema_json
    
    async def _fetch_schema(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetch table and column definitions with sample data.
        
        Returns:
            Dictionary of tables with columns and sample data
        """
        tables = {}
        
        async with (await get_conn()) as conn:
            # Get all table names
            table_rows = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            # Get columns for each table
            for table_row in table_rows:
                table_name = table_row["table_name"]
                
                # Get columns with data types
                column_rows = await conn.fetch("""
                    SELECT 
                        column_name, 
                        data_type,
                        is_nullable,
                        column_default,
                        ordinal_position
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = $1
                    ORDER BY ordinal_position
                """, table_name)
                
                columns = []
                for col in column_rows:
                    columns.append({
                        "name": col["column_name"],
                        "type": col["data_type"],
                        "nullable": col["is_nullable"] == "YES",
                        "default": col["column_default"],
                        "position": col["ordinal_position"]
                    })
                
                # Get primary key
                pk_rows = await conn.fetch("""
                    SELECT a.attname
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    WHERE i.indrelid = $1::regclass
                    AND i.indisprimary
                """, table_name)
                
                primary_keys = [row["attname"] for row in pk_rows]
                
                # Store table info
                tables[table_name] = {
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "sample": await self._get_sample_rows(conn, table_name)
                }
                
        return tables
    
    async def _fetch_relationships(self) -> List[Dict[str, Any]]:
        """
        Fetch foreign key relationships between tables.
        
        Returns:
            List of relationship dictionaries
        """
        relationships = []
        
        async with (await get_conn()) as conn:
            rel_rows = await conn.fetch("""
                SELECT
                    tc.table_schema, 
                    tc.constraint_name, 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
            """)
            
            for row in rel_rows:
                relationships.append({
                    "name": row["constraint_name"],
                    "table": row["table_name"],
                    "column": row["column_name"],
                    "referenced_table": row["foreign_table_name"],
                    "referenced_column": row["foreign_column_name"]
                })
                
        return relationships
    
    async def _fetch_table_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetch table statistics (row count, size).
        
        Returns:
            Dictionary of table statistics
        """
        stats = {}
        
        async with (await get_conn()) as conn:
            # Get row counts and sizes
            stat_rows = await conn.fetch("""
                SELECT
                    relname as table_name,
                    n_live_tup as row_count,
                    pg_size_pretty(pg_total_relation_size(C.oid)) as table_size
                FROM pg_class C
                LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
                WHERE nspname = 'public'
                AND C.relkind = 'r'
                ORDER BY n_live_tup DESC
            """)
            
            for row in stat_rows:
                stats[row["table_name"]] = {
                    "row_count": row["row_count"],
                    "table_size": row["table_size"]
                }
                
        return stats
    
    async def _get_sample_rows(self, conn, table_name: str) -> List[Dict[str, Any]]:
        """
        Get sample rows from a table.
        
        Args:
            conn: Database connection
            table_name: Name of the table
            
        Returns:
            List of sample rows as dictionaries
        """
        try:
            # Check table size first
            row_count = await conn.fetchval(
                "SELECT reltuples::bigint FROM pg_class WHERE relname = $1",
                table_name
            )
            
            # Skip sampling for huge tables
            if row_count and row_count > self.max_table_size:
                logger.info(f"Skipping sample data for large table {table_name} ({row_count} rows)")
                return []
            
            # Get sample rows
            sample_rows = await conn.fetch(
                f"SELECT * FROM {table_name} LIMIT {self.sample_rows}"
            )
            
            # Convert to dictionaries
            return [dict(row) for row in sample_rows]
            
        except Exception as e:
            logger.warning(f"Error getting sample data for table {table_name}: {e}")
            return []
    
    async def get_table_columns(self, table_name: str) -> List[str]:
        """
        Get column names for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column names
        """
        schema_json = await self.load_schema()
        schema = json.loads(schema_json)
        
        if table_name in schema["tables"]:
            return [col["name"] for col in schema["tables"][table_name]["columns"]]
        
        return []
    
    async def get_related_tables(self, table_name: str) -> List[str]:
        """
        Get tables related to the specified table through foreign keys.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of related table names
        """
        schema_json = await self.load_schema()
        schema = json.loads(schema_json)
        
        related = set()
        
        # Check relationships where table is on either side
        for rel in schema["relationships"]:
            if rel["table"] == table_name:
                related.add(rel["referenced_table"])
            elif rel["referenced_table"] == table_name:
                related.add(rel["table"])
                
        return list(related)
    
    async def refresh_schema(self) -> str:
        """
        Force a refresh of the schema cache.
        
        Returns:
            Refreshed schema as JSON string
        """
        return await self.load_schema(force_refresh=True)


# Singleton instance for global use
schema_service = SchemaService()

# Shorthand function for backward compatibility
async def load_schema() -> str:
    """Return cached schema JSON (tables → cols) + sample rows/table."""
    return await schema_service.load_schema()
