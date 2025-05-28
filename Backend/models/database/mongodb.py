"""
MongoDB Models and Schema Definitions for SynGen AI
Handles document storage, RAG operations, and unstructured data
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json

class DocumentType(Enum):
    """Types of documents stored in MongoDB"""
    POLICY = "policy"
    PROCEDURE = "procedure"
    GUIDELINE = "guideline"
    REPORT = "report"
    CHAT_HISTORY = "chat_history"
    QUERY_LOG = "query_log"
    USER_PREFERENCE = "user_preference"

class DocumentStatus(Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    ERROR = "error"

@dataclass
class PolicyDocument:
    """Policy document model for MongoDB"""
    filename: str
    title: str
    content: str
    content_type: str = DocumentType.POLICY.value
    
    # Processing metadata
    status: str = DocumentStatus.PENDING.value
    processing_info: Dict[str, Any] = None
    
    # Content metadata
    file_size: int = None
    page_count: int = None
    word_count: int = None
    language: str = "en"
    
    # Categorization
    categories: List[str] = None
    tags: List[str] = None
    department: str = None
    region: str = None
    
    # Version control
    version: str = "1.0"
    effective_date: datetime = None
    expiry_date: datetime = None
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    indexed_at: datetime = None
    
    # RAG specific fields
    chunks: List[Dict[str, Any]] = None  # Text chunks for RAG
    embeddings_status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.processing_info is None:
            self.processing_info = {}
        if self.categories is None:
            self.categories = []
        if self.tags is None:
            self.tags = []
        if self.chunks is None:
            self.chunks = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        # Convert datetime objects to ISO format
        for field in ['created_at', 'updated_at', 'indexed_at', 'effective_date', 'expiry_date']:
            if data[field]:
                data[field] = data[field].isoformat() if isinstance(data[field], datetime) else data[field]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PolicyDocument':
        """Create instance from MongoDB document"""
        # Convert ISO strings back to datetime
        for field in ['created_at', 'updated_at', 'indexed_at', 'effective_date', 'expiry_date']:
            if data.get(field):
                if isinstance(data[field], str):
                    try:
                        data[field] = datetime.fromisoformat(data[field])
                    except:
                        data[field] = None
        
        return cls(**data)

@dataclass
class ChatMessage:
    """Chat message model"""
    user_id: str
    session_id: str
    message: str
    message_type: str  # 'user', 'assistant', 'system'
    
    # Response metadata
    intent: str = None
    sql_query: str = None
    data_sources: List[str] = None
    response_time: float = None
    
    # Context
    context: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    # Timestamps
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.context is None:
            self.context = {}
        if self.metadata is None:
            self.metadata = {}
        if self.data_sources is None:
            self.data_sources = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        if data['timestamp']:
            data['timestamp'] = data['timestamp'].isoformat() if isinstance(data['timestamp'], datetime) else data['timestamp']
        return data

@dataclass
class QueryLog:
    """Query execution log"""
    user_id: str
    session_id: str
    query: str
    
    # Processing details
    intent: str = None
    sql_query: str = None
    results_count: int = 0
    response: str = None
    
    # Performance metrics
    processing_time: float = None
    sql_execution_time: float = None
    rag_retrieval_time: float = None
    
    # Data sources used
    tables_accessed: List[str] = None
    documents_referenced: List[str] = None
    
    # Success/failure tracking
    status: str = "success"  # success, error, timeout
    error_message: str = None
    
    # User context
    user_role: str = None
    user_region: str = None
    user_permissions: List[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.tables_accessed is None:
            self.tables_accessed = []
        if self.documents_referenced is None:
            self.documents_referenced = []
        if self.user_permissions is None:
            self.user_permissions = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        if data['timestamp']:
            data['timestamp'] = data['timestamp'].isoformat() if isinstance(data['timestamp'], datetime) else data['timestamp']
        return data

@dataclass
class UserPreferences:
    """User preferences and settings"""
    user_id: str
    
    # UI preferences
    theme: str = "light"
    language: str = "en"
    explanation_style: str = "business_analyst"
    
    # Query preferences
    default_row_limit: int = 100
    preferred_data_sources: List[str] = None
    notification_settings: Dict[str, bool] = None
    
    # Access controls
    role: str = "user"
    region: str = "global"
    permissions: List[str] = None
    department: str = None
    
    # Personalization
    favorite_queries: List[str] = None
    query_history_retention: int = 30  # days
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    last_login: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.preferred_data_sources is None:
            self.preferred_data_sources = []
        if self.notification_settings is None:
            self.notification_settings = {"email": True, "push": False}
        if self.permissions is None:
            self.permissions = ["read"]
        if self.favorite_queries is None:
            self.favorite_queries = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        # Convert datetime objects
        for field in ['created_at', 'updated_at', 'last_login']:
            if data[field]:
                data[field] = data[field].isoformat() if isinstance(data[field], datetime) else data[field]
        return data

@dataclass
class DocumentChunk:
    """Document chunk for RAG processing"""
    document_id: str
    chunk_index: int
    content: str
    
    # Chunk metadata
    start_position: int = 0
    end_position: int = 0
    word_count: int = 0
    
    # Embeddings
    embedding: List[float] = None
    embedding_model: str = None
    
    # Context
    section_title: str = None
    page_number: int = None
    context_before: str = None
    context_after: str = None
    
    # Processing metadata
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.embedding is None:
            self.embedding = []
        if not self.word_count:
            self.word_count = len(self.content.split())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat() if isinstance(data['created_at'], datetime) else data['created_at']
        return data

class MongoDBCollections:
    """Collection names for MongoDB"""
    POLICY_DOCUMENTS = "policy_documents"
    CHAT_HISTORY = "chat_history"
    QUERY_LOGS = "query_logs"
    USER_PREFERENCES = "user_preferences"
    DOCUMENT_CHUNKS = "document_chunks"
    SYSTEM_METRICS = "system_metrics"
    API_USAGE = "api_usage"

class MongoDBIndexes:
    """Index definitions for MongoDB collections"""
    
    @staticmethod
    def get_indexes() -> Dict[str, List[Dict]]:
        """Get all index definitions"""
        return {
            MongoDBCollections.POLICY_DOCUMENTS: [
                # Text search indexes
                {"key": {"title": "text", "content": "text", "filename": "text"}, "name": "text_search"},
                
                # Query optimization indexes
                {"key": {"content_type": 1}, "name": "content_type_idx"},
                {"key": {"status": 1}, "name": "status_idx"},
                {"key": {"created_at": -1}, "name": "created_at_desc_idx"},
                {"key": {"categories": 1}, "name": "categories_idx"},
                {"key": {"department": 1, "region": 1}, "name": "dept_region_idx"},
                
                # Compound indexes
                {"key": {"content_type": 1, "status": 1, "created_at": -1}, "name": "content_status_date_idx"},
            ],
            
            MongoDBCollections.CHAT_HISTORY: [
                {"key": {"user_id": 1, "session_id": 1, "timestamp": -1}, "name": "user_session_time_idx"},
                {"key": {"session_id": 1, "timestamp": 1}, "name": "session_chronological_idx"},
                {"key": {"user_id": 1, "timestamp": -1}, "name": "user_recent_idx"},
                {"key": {"message": "text"}, "name": "message_search_idx"},
            ],
            
            MongoDBCollections.QUERY_LOGS: [
                {"key": {"user_id": 1, "timestamp": -1}, "name": "user_recent_queries_idx"},
                {"key": {"session_id": 1, "timestamp": 1}, "name": "session_queries_idx"},
                {"key": {"status": 1, "timestamp": -1}, "name": "status_time_idx"},
                {"key": {"user_role": 1, "timestamp": -1}, "name": "role_time_idx"},
                {"key": {"sql_query": "text", "query": "text"}, "name": "query_search_idx"},
                
                # Performance monitoring
                {"key": {"processing_time": -1}, "name": "performance_idx"},
                {"key": {"tables_accessed": 1}, "name": "tables_accessed_idx"},
            ],
            
            MongoDBCollections.USER_PREFERENCES: [
                {"key": {"user_id": 1}, "name": "user_id_unique_idx", "unique": True},
                {"key": {"role": 1}, "name": "role_idx"},
                {"key": {"region": 1}, "name": "region_idx"},
                {"key": {"department": 1}, "name": "department_idx"},
                {"key": {"last_login": -1}, "name": "last_login_idx"},
            ],
            
            MongoDBCollections.DOCUMENT_CHUNKS: [
                {"key": {"document_id": 1, "chunk_index": 1}, "name": "doc_chunk_idx"},
                {"key": {"content": "text"}, "name": "chunk_content_search_idx"},
                {"key": {"embedding_model": 1}, "name": "embedding_model_idx"},
                {"key": {"word_count": -1}, "name": "word_count_idx"},
            ],
            
            MongoDBCollections.SYSTEM_METRICS: [
                {"key": {"timestamp": -1}, "name": "timestamp_desc_idx"},
                {"key": {"metric_type": 1, "timestamp": -1}, "name": "metric_type_time_idx"},
            ],
            
            MongoDBCollections.API_USAGE: [
                {"key": {"user_id": 1, "timestamp": -1}, "name": "user_usage_idx"},
                {"key": {"endpoint": 1, "timestamp": -1}, "name": "endpoint_usage_idx"},
                {"key": {"timestamp": -1}, "name": "usage_time_idx"},
            ]
        }

def create_sample_documents():
    """Create sample documents for testing"""
    
    # Sample policy document
    policy_doc = PolicyDocument(
        filename="sample_policy.pdf",
        title="Inventory Management Policy",
        content="""
        This policy outlines the procedures for managing inventory across all DataCo Global facilities.
        
        1. Inventory Classification:
        - Fast-moving items: Items with movement in the last 30 days
        - Slow-moving items: Items with movement in the last 90 days but not in the last 30 days
        - No-moving items: Items with no movement in the last 180 days
        
        2. Inventory Procedures:
        - Daily cycle counts for fast-moving items
        - Weekly counts for slow-moving items
        - Monthly full inventory for no-moving items
        
        3. Write-off Procedures:
        - Items with no movement for 365 days are eligible for write-off
        - Approval required from regional manager for write-offs over $10,000
        """,
        categories=["inventory", "operations"],
        tags=["policy", "procedures", "inventory-management"],
        department="Operations",
        region="Global",
        effective_date=datetime(2024, 1, 1),
        status=DocumentStatus.INDEXED.value
    )
    
    # Sample chat message
    chat_msg = ChatMessage(
        user_id="user123",
        session_id="session456",
        message="What is our policy on slow-moving inventory?",
        message_type="user",
        intent="document_search",
        context={"previous_queries": [], "user_role": "analyst"}
    )
    
    # Sample query log
    query_log = QueryLog(
        user_id="user123",
        session_id="session456",
        query="How many slow-moving items do we have?",
        intent="hybrid",
        sql_query="SELECT COUNT(*) FROM products WHERE last_movement_date BETWEEN '2024-01-01' AND '2024-03-01'",
        results_count=156,
        response="You have 156 slow-moving items based on our inventory classification policy.",
        processing_time=2.3,
        sql_execution_time=0.8,
        rag_retrieval_time=1.2,
        tables_accessed=["products", "inventory_movements"],
        documents_referenced=["Inventory Management Policy"],
        user_role="analyst",
        user_region="north-america",
        user_permissions=["read", "query"]
    )
    
    # Sample user preferences
    user_prefs = UserPreferences(
        user_id="user123",
        theme="dark",
        explanation_style="technical",
        default_row_limit=50,
        role="analyst",
        region="north-america",
        permissions=["read", "query", "export"],
        department="Operations",
        favorite_queries=["inventory levels", "sales by region"],
        last_login=datetime.now()
    )
    
    return {
        "policy_document": policy_doc,
        "chat_message": chat_msg,
        "query_log": query_log,
        "user_preferences": user_prefs
    }

if __name__ == "__main__":
    # Test the models
    samples = create_sample_documents()
    
    print("📄 Sample Policy Document:")
    print(json.dumps(samples["policy_document"].to_dict(), indent=2, default=str))
    
    print("\n💬 Sample Chat Message:")
    print(json.dumps(samples["chat_message"].to_dict(), indent=2, default=str))
    
    print("\n📊 Sample Query Log:")
    print(json.dumps(samples["query_log"].to_dict(), indent=2, default=str))
    
    print("\n⚙️ Sample User Preferences:")
    print(json.dumps(samples["user_preferences"].to_dict(), indent=2, default=str))
    
    print("\n🗂️ MongoDB Collections:")
    for collection in [attr for attr in dir(MongoDBCollections) if not attr.startswith('_')]:
        print(f"  - {getattr(MongoDBCollections, collection)}")
    
    print("\n📊 Index Definitions:")
    indexes = MongoDBIndexes.get_indexes()
    for collection, collection_indexes in indexes.items():
        print(f"  {collection}: {len(collection_indexes)} indexes")
        for idx in collection_indexes:
            print(f"    - {idx['name']}: {idx['key']}")