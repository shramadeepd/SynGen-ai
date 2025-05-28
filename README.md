# SynGen AI - Intelligent Text-to-SQL Platform

> **Transform natural language questions into powerful SQL queries with enterprise-grade security and multi-agent intelligence**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Agno](https://img.shields.io/badge/Framework-Agno-green.svg)](https://agno.ai)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-red.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Cache-Redis-red.svg)](https://redis.io)

## 🌟 Overview

SynGen AI is a production-ready, intelligent Text-to-SQL system that converts natural language questions into accurate SQL queries. Built with a **multi-agent architecture** using the Agno framework, it provides enterprise-grade security, intelligent error handling, governance features, and comprehensive document retrieval capabilities.

### 🎯 What Does This System Do?

Instead of writing complex SQL queries, users can simply ask questions like:
- "How many orders were placed last month?"
- "Who are our top 5 customers by sales revenue?"
- "Show me products with low inventory levels"
- "What is our company policy on returns?" (RAG document search)

The system intelligently converts these questions into proper SQL queries, executes them safely, and provides clear explanations of the results in natural language.

## 🏗️ System Architecture

Our system uses a **multi-agent orchestration pattern** where specialized AI agents work together:

```
User Question → Intent Router → SQL Generator → Validator → Executor → Result Explainer → User
                      ↓              ↓            ↓           ↓            ↓
                  Route Query    Generate SQL   Validate   Execute    Explain Results
                 (SQL/Doc/Chat)  (with Context) (Security)  (Safely)   (Natural Language)
```

### 🤖 Core Agents

1. **Intent Router Agent** - Classifies user queries and routes them appropriately
2. **SQL Generator Agent** - Converts natural language to SQL using schema context
3. **SQL Validator Agent** - Validates queries for security and compliance  
4. **SQL Critic Agent** - Fixes broken queries automatically
5. **Result Explainer Agent** - Explains results in business-friendly language

## 📁 Project Structure

```
SynGen-ai/
├── Backend/                        # Production-level Backend application
│   ├── api/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── routes/                 # API route definitions
│   │   ├── middleware/             # Custom middleware components
│   │   └── dependencies/           # Dependency injection modules
│   ├── agents/                     # Specialized AI agents
│   │   ├── __init__.py             # Agent exports and configurations
│   │   ├── intent_router.py        # Query intent classification
│   │   ├── sql_generator.py        # Natural language to SQL conversion
│   │   ├── sql_validator.py        # Security validation and compliance
│   │   ├── sql_critic.py           # Error analysis and automatic fixing
│   │   └── result_explainer.py     # Natural language result explanation
│   ├── core/                       # Core framework components
│   │   ├── logging.py              # Structured logging and monitoring
│   │   └── security.py             # JWT authentication and authorization
│   ├── services/                   # Business logic services
│   │   ├── ai/                     # AI-powered services
│   │   │   ├── txt_to_sql.py       # Main orchestrator and workflow
│   │   │   ├── rag.py              # Document search and RAG functionality
│   │   │   └── sql_templates.py    # SQL generation templates
│   │   ├── data/                   # Data processing services
│   │   │   └── dual_db_loader.py   # Dual database data loader
│   │   └── database/               # Database services
│   │       ├── db.py               # Database connections and schema service
│   │       └── database_manager.py # Dual database manager
│   ├── models/                     # Data models
│   │   ├── database/               # Database model definitions
│   │   │   ├── postgresql.py       # PostgreSQL ORM models
│   │   │   └── mongodb.py          # MongoDB document models
│   │   └── schemas/                # Pydantic request/response schemas
│   │       └── models.py           # API data models
│   ├── config/                     # Configuration management
│   │   └── settings.py             # Application settings
│   ├── scripts/                    # Utility scripts
│   │   ├── load_csv_data.py        # CSV data loading script
│   │   ├── load_pdf_documents.py   # PDF document processing
│   │   ├── setup_database.py       # Database initialization
│   │   └── test_system.py          # System testing script
│   ├── utils/                      # Utility modules
│   │   ├── text/                   # Text processing utilities
│   │   └── validation/             # Data validation utilities
│   └── tests/                      # Comprehensive test suite
│       ├── test_agents_simple.py   # Agent functionality tests
│       ├── test_database_simple.py # Database operation tests
│       ├── conftest.py             # Test configuration
│       └── run_tests.py            # Test runner script
├── Document_Repository(dataco-global-policy-dataset)/  # Policy documents for RAG
├── Supply_chain_database(dataco-supply-chain-dataset)/ # Sample dataset
├── pyproject.toml                  # Modern Python project configuration
├── postman_guide.md                # Comprehensive API testing guide
├── example.env                     # Environment configuration template
├── TODO.txt                        # Development task list
├── SUMMARY.md                      # Detailed codebase summary
└── README.md                       # This comprehensive documentation
```

---

## 🔧 Installation and Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 14+ with pgvector extension
- Redis 6+
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SynGen-ai
```

### 2. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Database Setup

#### PostgreSQL with Sample Data

```bash
# Create database
createdb syngen_ai

# Load sample schema and data
psql -d syngen_ai -f Backend/application/schema.sql

# Enable pgvector extension (for future vector operations)
psql -d syngen_ai -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

#### Redis Setup

```bash
# Start Redis server
redis-server

# Verify Redis is running
redis-cli ping
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Database connections
DATABASE_URL=postgresql://username:password@localhost:5432/syngen_ai
RO_DATABASE_URL=postgresql://readonly_user:password@localhost:5432/syngen_ai

# Redis configuration
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET=your_secure_secret_key_here_change_in_production

# AI/LLM Configuration (Optional - for Gemini)
GEMINI_API_KEY=your_gemini_api_key_here

# Logging
LOG_LEVEL=INFO

# Service configuration
HOST=0.0.0.0
PORT=8000

# Schema caching
SCHEMA_CACHE_TTL=600
SCHEMA_SAMPLE_ROWS=5
SCHEMA_MAX_TABLE_SIZE=1000000
```

### 5. Database Schema Creation

The system includes a comprehensive supply chain database schema. Run the following to create all tables:

```bash
cd Backend
python -c "
from application.models import Base, engine
Base.metadata.create_all(bind=engine)
print('Database schema created successfully!')
"
```

---

## 🚀 Quick Start

### 1. Start the Application

```bash
cd Backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Root**: http://localhost:8000/

### 2. Authentication

First, get an access token:

```bash
curl -X POST "http://localhost:8000/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
```

This returns a JWT token that you'll use for subsequent requests.

### 3. Basic Usage Examples

#### Simple SQL Query

```bash
curl -X POST "http://localhost:8000/api/sql" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question": "How many orders were placed last month?"}'
```

#### Document Search (RAG)

```bash
curl -X POST "http://localhost:8000/api/rag/query" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is our return policy?"}'
```

#### Add Document to RAG

```bash
curl -X POST "http://localhost:8000/api/rag/ingest" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "document": "Company policy text here...",
       "metadata": {"source": "policy_manual", "date": "2024-01-01"}
     }'
```

---

## 📖 Detailed Component Documentation

### Core Components

#### 1. FastAPI Application (`app.py`)

**Purpose**: Main application entry point that sets up API routes, middleware, and request handling.

**Key Features**:
- CORS middleware for cross-origin requests
- JWT-based authentication and authorization
- Request/response logging with unique request IDs
- Error handling with structured error responses
- Health check endpoints
- Rate limiting and security middleware

**Key Classes and Functions**:

##### `Token` (Pydantic Model)
```python
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

##### `UserLogin` (Pydantic Model)
```python
class UserLogin(BaseModel):
    username: str
    password: str
```

##### `UserRegistration` (Pydantic Model)
```python
class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "user"
    region: Optional[str] = None
```

**Main API Endpoints**:
- `POST /api/sql` - Text-to-SQL conversion and execution
- `POST /api/rag/query` - Document search and question answering
- `POST /api/rag/ingest` - Add documents to the knowledge base
- `POST /auth/token` - User authentication
- `GET /auth/me` - Get current user information
- `GET /health` - Application health check

#### 2. Database Service (`core/db.py`)

**Purpose**: Provides database connection management and comprehensive schema introspection services.

**Key Classes**:

##### `SchemaService`
Advanced database schema introspection with intelligent caching.

**Key Methods**:

###### `load_schema(force_refresh=False) → str`
- **Purpose**: Loads complete database schema with Redis caching
- **Returns**: JSON string containing tables, columns, relationships, and sample data
- **Features**: 
  - Automatic relationship detection via foreign keys
  - Sample data extraction for AI context
  - Configurable TTL caching
  - Performance metrics and logging

###### `_fetch_schema() → Dict[str, Dict[str, Any]]`
- **Purpose**: Retrieves detailed table and column information
- **Features**:
  - Column data types and constraints
  - Primary key identification
  - Sample rows for AI context
  - Null/default value information

###### `_fetch_relationships() → List[Dict[str, Any]]`
- **Purpose**: Maps foreign key relationships between tables
- **Returns**: List of relationship objects with source and target information

###### `get_table_columns(table_name) → List[str]`
- **Purpose**: Get column names for a specific table
- **Use Case**: Dynamic query building and validation

###### `get_related_tables(table_name) → List[str]`
- **Purpose**: Find tables connected via foreign key relationships
- **Use Case**: Context expansion for complex queries

**Database Connection Functions**:
- `get_ro_conn()` - Read-only database connection
- `get_rw_conn()` - Read-write database connection  
- `db_transaction()` - Context manager for transactions

#### 3. Security Service (`core/security.py`)

**Purpose**: Handles JWT-based authentication, authorization, and security controls.

**Key Functions**:

##### `create_access_token(data, expires_delta) → str`
- **Purpose**: Creates signed JWT tokens with user claims
- **Parameters**:
  - `data`: User information (username, role, region, permissions)
  - `expires_delta`: Token expiration time
- **Returns**: Encoded JWT string

##### `current_user(creds) → Dict[str, Any]`
- **Purpose**: FastAPI dependency to extract and validate current user
- **Features**:
  - Token signature validation
  - Expiration checking
  - User context extraction
- **Returns**: User information dictionary

##### `role_required(allowed_roles) → Callable`
- **Purpose**: Dependency factory for role-based access control
- **Usage**: `@app.get("/admin", dependencies=[Depends(role_required(["admin"]))])`

##### `has_permission(required_permission) → Callable`
- **Purpose**: Dependency factory for permission-based access control
- **Features**: Fine-grained permission checking beyond roles

#### 4. Logging Service (`core/logging.py`)

**Purpose**: Provides structured logging with request tracing and performance monitoring.

**Key Classes**:

##### `LogContext`
Context manager for request-scoped logging with consistent request tracking.

**Key Methods**:
- `log_info(message, extra)` - Info level logging with context
- `log_error(message, extra)` - Error level logging with context
- `log_exception(exception, extra)` - Exception logging with traceback
- `log_warning(message, extra)` - Warning level logging with context

##### `QueryLogger`
Specialized logger for SQL query execution metrics.

**Key Methods**:
- `log_query(query, duration_ms, rows_returned, user_id, question)` - Log query performance
- `log_error(query, error, user_id)` - Log query execution errors

**Decorators**:
- `@log_execution_time` - Decorator to automatically log function execution time

---

### Agent System (`feature/agents/`)

#### 1. Intent Router Agent (`intent_router.py`)

**Purpose**: Classifies user queries to determine the appropriate processing pipeline.

**Key Enums**:

##### `QueryIntent`
```python
class QueryIntent(Enum):
    SQL_QUERY = "sql_query"           # Data retrieval from database
    DOCUMENT_SEARCH = "document_search" # Information from documents
    GENERAL_CHAT = "general_chat"     # Conversational queries
    HYBRID = "hybrid"                 # Requires both SQL and documents
    UNKNOWN = "unknown"               # Cannot classify
```

**Key Classes**:

##### `IntentResult`
```python
@dataclass
class IntentResult:
    intent: QueryIntent
    confidence: float
    reasoning: str
    suggested_approach: str
    metadata: Dict[str, Any]
```

##### `IntentRouterAgent`
**Main Methods**:

###### `classify_intent(query, context) → IntentResult`
- **Purpose**: Analyzes user query and determines intent
- **Process**:
  1. Quick pattern matching for obvious intents
  2. AI-powered analysis for complex queries
  3. Confidence scoring and reasoning generation
- **Returns**: Detailed intent classification with confidence scores

###### `_classify_by_patterns(query) → IntentResult`
- **Purpose**: Fast classification using keyword patterns
- **Features**: 
  - SQL patterns: "how many", "total", "average", "list all"
  - Document patterns: "policy", "procedure", "what is"
  - Chat patterns: "hello", "thank you", "help me"

###### `_classify_by_llm(query, context) → IntentResult`
- **Purpose**: Advanced AI-powered intent classification
- **Use Cases**: Complex or ambiguous queries requiring understanding

#### 2. SQL Generator Agent (`sql_generator.py`)

**Purpose**: Converts natural language questions into syntactically correct and contextually appropriate SQL queries.

**Key Classes**:

##### `SQLGenerationRequest`
```python
@dataclass
class SQLGenerationRequest:
    query: str                        # Natural language question
    user_context: Optional[Dict]      # User info (role, region, permissions)
    schema_tables: Optional[List]     # Specific tables to focus on
    constraints: Optional[List]       # Additional rules to follow
    examples: Optional[List]          # Similar examples for few-shot learning
    metadata: Optional[Dict]          # Extra context information
```

##### `SQLGenerationResult`
```python
@dataclass
class SQLGenerationResult:
    sql: str                         # Generated SQL query
    confidence: float                # Confidence in the generated SQL
    reasoning: str                   # Explanation of the SQL generation
    tables_used: List[str]           # Database tables referenced
    estimated_cost: Optional[float]  # Estimated execution cost
    warnings: List[str]              # Potential issues or limitations
    metadata: Optional[Dict]         # Additional generation information
```

##### `SQLGeneratorAgent`
**Main Methods**:

###### `generate_sql(request) → SQLGenerationResult`
- **Purpose**: Main SQL generation pipeline
- **Process**:
  1. Load and filter database schema
  2. Select relevant few-shot examples
  3. Build comprehensive AI prompt
  4. Generate SQL using LLM
  5. Extract metadata and confidence scoring
- **Features**:
  - Schema-aware generation
  - Few-shot learning from examples
  - User context integration
  - Cost estimation

###### `_filter_schema(schema_data, focus_tables) → Dict`
- **Purpose**: Reduces schema to relevant tables for better AI performance
- **Benefits**: Improved accuracy and reduced token usage

###### `_select_examples(query) → List[Dict]`
- **Purpose**: Finds most relevant example queries for few-shot learning
- **Algorithm**: Semantic similarity scoring based on shared keywords

#### 3. SQL Validator Agent (`sql_validator.py`)

**Purpose**: Ensures generated SQL queries are secure, compliant, and safe to execute.

**Key Enums**:

##### `ValidationLevel`
```python
class ValidationLevel(Enum):
    STRICT = "strict"           # Maximum security (basic users)
    MODERATE = "moderate"       # Balanced security (business users)
    RELAXED = "relaxed"         # Minimal restrictions (analysts)
    ADMIN = "admin"             # Administrative access
```

##### `SecurityThreat`
```python
class SecurityThreat(Enum):
    SQL_INJECTION = "sql_injection"
    UNAUTHORIZED_OPERATION = "unauthorized_operation"
    FORBIDDEN_TABLE = "forbidden_table"
    EXCESSIVE_COST = "excessive_cost"
    MALFORMED_QUERY = "malformed_query"
    PERMISSION_VIOLATION = "permission_violation"
```

**Key Classes**:

##### `ValidationResult`
```python
@dataclass
class ValidationResult:
    is_valid: bool                      # Whether SQL passed all checks
    sql_clean: str                      # Cleaned/sanitized SQL
    threats_detected: List[SecurityThreat]  # Security issues found
    warnings: List[str]                 # Non-blocking warnings
    suggestions: List[str]              # Performance improvement suggestions
    metadata: Dict[str, Any]            # Additional validation information
```

##### `SQLValidatorAgent`
**Main Methods**:

###### `validate_sql(sql, user_context, validation_level) → ValidationResult`
- **Purpose**: Comprehensive SQL security validation
- **Validation Steps**:
  1. Syntax validation using SQL parser
  2. Security threat detection
  3. Permission validation
  4. Cost analysis and limits
  5. Result sanitization

###### `_validate_syntax(sql, result)`
- **Purpose**: Ensures SQL is well-formed and only contains SELECT statements
- **Tools**: Uses `sqlglot` for AST parsing and validation

###### `_detect_security_threats(sql, result, level)`
- **Purpose**: Scans for malicious patterns and injection attempts
- **Patterns**: Detects dangerous operations, injection vectors, and forbidden patterns

###### `_validate_permissions(sql, result, user_context)`
- **Purpose**: Ensures user has permission to access requested data
- **Features**: Role-based table access and regional restrictions

#### 4. SQL Critic Agent (`sql_critic.py`)

**Purpose**: Analyzes failed SQL queries, identifies root causes, and generates automatic fixes.

**Key Enums**:

##### `ErrorType`
```python
class ErrorType(Enum):
    SYNTAX_ERROR = "syntax_error"           # SQL grammar mistakes
    SEMANTIC_ERROR = "semantic_error"       # Valid SQL but wrong meaning
    PERMISSION_ERROR = "permission_error"   # User lacks access
    PERFORMANCE_ERROR = "performance_error" # Query too slow/expensive
    LOGIC_ERROR = "logic_error"             # SQL doesn't match intent
    DATA_TYPE_ERROR = "data_type_error"     # Wrong data types
    UNKNOWN_ERROR = "unknown_error"         # Unclassified error
```

##### `FixStrategy`
```python
class FixStrategy(Enum):
    SYNTAX_CORRECTION = "syntax_correction"
    SCHEMA_ALIGNMENT = "schema_alignment"
    PERMISSION_ADJUSTMENT = "permission_adjustment"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    LOGIC_REFINEMENT = "logic_refinement"
    TYPE_CASTING = "type_casting"
    COMPREHENSIVE_REWRITE = "comprehensive_rewrite"
```

**Key Classes**:

##### `ErrorAnalysis`
```python
@dataclass
class ErrorAnalysis:
    error_type: ErrorType               # Classification of the error
    error_message: str                  # Original database error message
    root_cause: str                     # Analysis of why error occurred
    affected_components: List[str]      # Which parts of SQL are broken
    fix_strategy: FixStrategy           # Recommended approach to fix
    confidence: float                   # Confidence in the analysis
```

##### `FixResult`
```python
@dataclass
class FixResult:
    fixed_sql: str                      # The corrected SQL query
    fix_applied: FixStrategy            # Type of fix that was applied
    success_probability: float          # Likelihood this fix will work
    changes_made: List[str]             # Specific changes that were made
    explanation: str                    # Human-readable fix explanation
    metadata: Dict[str, Any]            # Additional fix information
```

##### `SQLCriticAgent`
**Main Methods**:

###### `analyze_and_fix(failed_sql, error_message, schema_context, user_intent) → FixResult`
- **Purpose**: Complete error analysis and fix generation pipeline
- **Process**:
  1. Error classification and root cause analysis
  2. Fix strategy selection
  3. AI-powered fix generation
  4. Success probability estimation

###### `_analyze_error(failed_sql, error_message, schema_context) → ErrorAnalysis`
- **Purpose**: Deep analysis of SQL errors
- **Features**:
  - Pattern-based quick classification
  - AI-powered complex error analysis
  - Root cause identification

#### 5. Result Explainer Agent (`result_explainer.py`)

**Purpose**: Converts SQL query results into clear, natural language explanations tailored to different audiences.

**Key Enums**:

##### `ExplanationStyle`
```python
class ExplanationStyle(Enum):
    EXECUTIVE_SUMMARY = "executive_summary"     # High-level insights
    BUSINESS_ANALYST = "business_analyst"       # Detailed analysis
    OPERATIONAL = "operational"                 # Actionable insights
    TECHNICAL = "technical"                     # Technical details
    CONVERSATIONAL = "conversational"          # Natural conversation
```

##### `InsightType`
```python
class InsightType(Enum):
    TREND = "trend"                   # Patterns over time
    ANOMALY = "anomaly"               # Unusual values or outliers
    COMPARISON = "comparison"         # Differences between groups
    DISTRIBUTION = "distribution"     # How values are spread
    CORRELATION = "correlation"       # Relationships between variables
    THRESHOLD = "threshold"           # Values above/below limits
    RANKING = "ranking"               # Top/bottom performers
```

**Key Classes**:

##### `DataInsight`
```python
@dataclass
class DataInsight:
    insight_type: InsightType           # Type of insight discovered
    description: str                    # Human-readable description
    significance: float                 # Importance score (0.0 to 1.0)
    data_points: List[Any]              # Supporting data points
    recommendation: Optional[str]       # Suggested action
```

##### `ExplanationResult`
```python
@dataclass
class ExplanationResult:
    natural_language: str               # Main explanation in plain English
    key_insights: List[DataInsight]     # Important discoveries
    data_summary: Dict[str, Any]        # Statistical summary
    business_impact: str                # Business implications
    recommendations: List[str]          # Suggested actions
    metadata: Dict[str, Any]            # Additional context
```

##### `ResultExplainerAgent`
**Main Methods**:

###### `explain_results(sql_query, results, user_question, style, context) → ExplanationResult`
- **Purpose**: Complete result explanation pipeline
- **Process**:
  1. Statistical analysis of results
  2. Automatic insight discovery
  3. Natural language generation
  4. Business impact assessment
  5. Recommendation generation

###### `_analyze_data_statistics(df) → Dict[str, Any]`
- **Purpose**: Comprehensive statistical analysis
- **Features**: Count, mean, median, null values, data types

###### `_discover_insights(df, sql_query, user_question) → List[DataInsight]`
- **Purpose**: Automatic pattern and insight discovery
- **Algorithms**: Trend analysis, anomaly detection, ranking analysis

---

### Main Orchestrator (`feature/txt_to_sql.py`)

#### `Text2SQLOrchestrator`

**Purpose**: Central coordinator that manages the complete Text-to-SQL pipeline using all specialized agents.

**Key Classes**:

##### `ExecutionStatus`
```python
class ExecutionStatus(Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    VALIDATION_FAILED = "validation_failed"
    EXECUTION_FAILED = "execution_failed"
    INTENT_MISMATCH = "intent_mismatch"
    SECURITY_VIOLATION = "security_violation"
    QUOTA_EXCEEDED = "quota_exceeded"
    UNKNOWN_ERROR = "unknown_error"
```

##### `Text2SQLRequest`
```python
@dataclass
class Text2SQLRequest:
    query: str                          # Natural language question
    user_context: Optional[Dict]        # User information
    preferences: Optional[Dict]         # User preferences
    session_context: Optional[Dict]     # Conversation history
    execution_options: Optional[Dict]   # Query execution options
```

##### `Text2SQLResponse`
```python
@dataclass
class Text2SQLResponse:
    status: ExecutionStatus             # Overall execution status
    sql_query: Optional[str]            # Generated SQL query
    results: Optional[List[Dict]]       # Query execution results
    explanation: Optional[str]          # Natural language explanation
    intent_analysis: Optional[Dict]     # Intent classification details
    validation_report: Optional[Dict]   # Security validation results
    execution_metrics: Optional[Dict]   # Performance metrics
    recommendations: Optional[List[str]] # Suggested actions
    metadata: Optional[Dict]            # Additional processing info
```

**Main Methods**:

##### `process_query(request) → Text2SQLResponse`
- **Purpose**: Complete query processing pipeline
- **Workflow**:
  1. Intent classification
  2. Request routing
  3. SQL generation
  4. Security validation
  5. Automatic error fixing
  6. Safe execution
  7. Result explanation
  8. Response compilation

---

### RAG System (`feature/rag.py`)

#### `RAGService`

**Purpose**: Provides document search and retrieval-augmented generation capabilities.

**Key Methods**:

##### `add_document(document, metadata)`
- **Purpose**: Process and index documents for search
- **Features**:
  - Text chunking with overlap
  - Embedding generation
  - Metadata preservation
  - Redis storage

##### `query(question, k=3) → Dict`
- **Purpose**: Search documents and generate answers
- **Process**:
  1. Query embedding generation
  2. Similarity search
  3. Context building
  4. AI-powered answer generation

##### `_chunk_text(text) → List[str]`
- **Purpose**: Split documents into searchable chunks
- **Features**: Intelligent sentence boundary detection

##### `_similarity_search(query_embedding, k) → List[Dict]`
- **Purpose**: Find most relevant document chunks
- **Algorithm**: Cosine similarity scoring

---

## 🗄️ Database Schema (`application/models.py`)

The system includes a comprehensive supply chain database with the following tables:

### Core Tables

#### Geographic Hierarchy
- **Countries** - Country definitions
- **States** - State/province information with regions
- **Cities** - City data with geographic coordinates
- **Addresses** - Street addresses with postal codes

#### Customer Management
- **Customers** - Customer profiles and segments
  - Primary fields: `customer_id`, `first_name`, `last_name`, `email`, `segment`
  - Business fields: `sales_per_customer`
  - Relationships: Links to addresses

#### Product Catalog
- **Categories** - Product category definitions
- **Departments** - Product department organization
- **Products** - Complete product catalog
  - Primary fields: `product_id`, `name`, `description`, `price`
  - Classifications: Links to categories and departments
  - Status tracking and image URLs

#### Order Management
- **Orders** - Order transactions and tracking
  - Primary fields: `order_id`, `customer_id`, `order_date`
  - Shipping: `shipping_date`, `scheduled_days`, `actual_days`
  - Business metrics: `benefit_per_order`, `late_delivery_risk`
  - Relationships: Customer, payment, delivery status, shipping mode

- **OrderItems** - Individual items within orders
  - Primary fields: `order_item_id`, `order_id`, `product_id`
  - Pricing: `product_price`, `discount_amount`, `discount_rate`
  - Metrics: `sales`, `total`, `profit_ratio`

#### Reference Data
- **PaymentTypes** - Payment method definitions
- **DeliveryStatuses** - Shipping status categories
- **ShippingModes** - Shipping method options
- **Markets** - Market segment classifications

### Key Relationships

The schema includes comprehensive foreign key relationships:
- Customers → Addresses → Cities → States → Countries
- Orders → Customers, PaymentTypes, DeliveryStatuses, ShippingModes, Markets
- OrderItems → Orders, Products
- Products → Categories, Departments

---

## 🛡️ Security and Governance

### Multi-Layer Security

#### 1. Authentication & Authorization
- **JWT-based authentication** with role and region claims
- **Role-based access control (RBAC)** with multiple permission levels
- **Regional access controls** for geo-fencing
- **Token expiration and refresh** mechanisms

#### 2. SQL Security Validation
- **Pattern-based threat detection** for injection attempts
- **AST parsing validation** to ensure only SELECT statements
- **Table access controls** based on user permissions
- **Query cost analysis** to prevent expensive operations
- **Result row limiting** to protect against data exfiltration

#### 3. Input Validation
- **Pydantic models** for request/response validation
- **SQL parameterization** to prevent injection
- **Content sanitization** for all user inputs
- **Rate limiting** on API endpoints

### Compliance Features

#### Data Governance
- **Row-level security** policies in PostgreSQL
- **Column-level access controls** based on user roles
- **Audit logging** of all query executions
- **Data masking** for sensitive information

#### Security Monitoring
- **Request tracing** with unique request IDs
- **Performance monitoring** and alerting
- **Error tracking** and analysis
- **Security violation logging**

---

## 🧪 Testing

### Test Structure (`tests/test_txt_to_sql.py`)

#### Test Categories

1. **Agent Unit Tests**
   - Intent router classification accuracy
   - SQL generator query quality
   - Validator security detection
   - Critic error fixing
   - Explainer natural language generation

2. **Integration Tests**
   - End-to-end workflow testing
   - Error handling and recovery
   - Security validation enforcement

3. **Performance Tests**
   - Concurrent request handling
   - Memory usage monitoring
   - Response time optimization

4. **Security Tests**
   - Malicious query blocking
   - Authorization enforcement
   - Data access controls

### Running Tests

```bash
cd Backend
pytest tests/ -v
```

### Test Coverage

```bash
pytest --cov=feature --cov-report=html tests/
```

---

## 📊 Monitoring and Observability

### Metrics and Logging

#### Application Metrics
- Request count and response times
- Success/failure rates
- SQL query execution times
- Agent performance statistics
- Security violation counts

#### Performance Monitoring
- Database connection pool usage
- Redis cache hit rates
- Memory and CPU utilization
- Queue depths and processing times

#### Structured Logging
```python
# Example log entry structure
{
    "timestamp": "2024-01-01T12:00:00Z",
    "level": "INFO",
    "request_id": "req_123456",
    "user_id": "user_789",
    "event": "sql_query_executed",
    "data": {
        "query": "SELECT COUNT(*) FROM orders",
        "execution_time_ms": 150,
        "rows_returned": 1,
        "tables_accessed": ["orders"]
    }
}
```

### Health Checks

#### Endpoint: `GET /health`
```json
{
    "status": "healthy",
    "database": "connected",
    "redis": "connected",
    "agents": "initialized",
    "uptime": "2h 30m",
    "version": "1.0.0"
}
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/syngen_ai
RO_DATABASE_URL=postgresql://readonly:password@localhost:5432/syngen_ai

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security Configuration
JWT_SECRET=your_secure_secret_key_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI/LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
DEFAULT_MODEL=gemini-2.0-flash-exp

# Service Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Schema Service Configuration
SCHEMA_CACHE_TTL=600
SCHEMA_SAMPLE_ROWS=5
SCHEMA_MAX_TABLE_SIZE=1000000

# Performance Configuration
MAX_QUERY_COST=1000000
DEFAULT_VALIDATION_LEVEL=moderate
QUERY_TIMEOUT=30
MAX_RESULT_ROWS=1000

# Agent Configuration
MAX_FIX_ATTEMPTS=3
ENABLE_SEMANTIC_CACHE=true
ENABLE_GOVERNANCE=true
```

### Custom Agent Configuration

```python
# Custom orchestrator setup
from feature.txt_to_sql import Text2SQLOrchestrator
from feature.agents import ValidationLevel

orchestrator = Text2SQLOrchestrator(
    model_name="gemini-2.0-flash-exp",
    default_validation_level=ValidationLevel.MODERATE,
    max_fix_attempts=3,
    enable_semantic_cache=True,
    enable_governance=True
)
```

---

## 🚀 Advanced Usage

### 1. Direct Agent Usage

```python
# Use individual agents for specific tasks
from feature.agents import (
    IntentRouterAgent, SQLGeneratorAgent, SQLValidatorAgent,
    SQLCriticAgent, ResultExplainerAgent
)

# Intent classification
router = IntentRouterAgent()
intent = await router.classify_intent("What is our return policy?")

# SQL generation
generator = SQLGeneratorAgent()
sql_result = await generator.generate_sql(request)

# SQL validation
validator = SQLValidatorAgent()
validation = await validator.validate_sql(sql_result.sql)

# Result explanation
explainer = ResultExplainerAgent()
explanation = await explainer.explain_results(sql, results, question)
```

### 2. Custom Validation Rules

```python
from feature.agents import SQLValidatorAgent, ValidationLevel

# Create validator with custom rules
validator = SQLValidatorAgent(
    validation_level=ValidationLevel.CUSTOM,
    max_query_cost=500000,
    allowed_tables={"orders", "customers", "products"},
    forbidden_patterns=["UNION", "EXEC", "sp_"]
)
```

### 3. Multi-Step Workflows

```python
from feature.txt_to_sql import Text2SQLRequest, Text2SQLOrchestrator

# Complex request with full context
request = Text2SQLRequest(
    query="Show me sales trends for the last quarter",
    user_context={
        "role": "manager",
        "region": "north-america",
        "permissions": ["read_sales", "read_orders"]
    },
    preferences={
        "explanation_style": "executive_summary",
        "performance_focused": True
    },
    session_context={
        "previous_queries": ["monthly sales", "customer segments"],
        "conversation_id": "conv_123"
    }
)

response = await orchestrator.process_query(request)
```

---

## 🐳 Docker Deployment

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.9'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://syngen:syngen@db:5432/syngen_ai
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=your_secure_secret_key
    depends_on:
      - db
      - redis
    volumes:
      - ./Backend:/app
      - ./Document_Repository:/app/documents

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: syngen_ai
      POSTGRES_USER: syngen
      POSTGRES_PASSWORD: syngen
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  redis_data:
```

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY Backend/ ./

# Create necessary directories
RUN mkdir -p logs documents

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

---

## ☁️ Cloud Deployment (GCP)

### 1. Google Cloud SQL Setup

```bash
# Create Cloud SQL instance
gcloud sql instances create syngen-ai-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create syngen_ai \
    --instance=syngen-ai-db

# Create users
gcloud sql users create syngen \
    --instance=syngen-ai-db \
    --password=secure_password
```

### 2. Google Cloud Run Deployment

```bash
# Build and push container
gcloud builds submit --tag gcr.io/your-project/syngen-ai

# Deploy to Cloud Run
gcloud run deploy syngen-ai \
    --image gcr.io/your-project/syngen-ai \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL=postgresql://...,REDIS_URL=redis://...
```

### 3. Memorystore (Redis) Setup

```bash
# Create Redis instance
gcloud redis instances create syngen-cache \
    --size=1 \
    --region=us-central1
```

---

## 📈 Performance Optimization

### Database Optimization

#### Indexing Strategy
```sql
-- Key indexes for query performance
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_customers_segment ON customers(segment);
CREATE INDEX idx_products_category ON products(category_id);

-- Composite indexes for common queries
CREATE INDEX idx_orders_date_status ON orders(order_date, delivery_status_id);
CREATE INDEX idx_order_items_product_date ON order_items(product_id, order_date);
```

#### Query Optimization
- Use connection pooling with asyncpg
- Implement query result caching in Redis
- Optimize schema loading with TTL caching
- Use read replicas for query execution

### Application Performance

#### Caching Strategy
```python
# Schema caching
SCHEMA_CACHE_TTL = 600  # 10 minutes

# Query result caching
QUERY_CACHE_TTL = 300   # 5 minutes

# Semantic caching for similar queries
SEMANTIC_CACHE_TTL = 3600  # 1 hour
```

#### Async Operations
- All database operations use async/await
- Concurrent agent processing where possible
- Background task processing for document ingestion
- Non-blocking AI model calls

---

## 🤝 Contributing

### Development Guidelines

1. **Code Style**
   - Follow PEP 8 for Python code formatting
   - Use type hints for all function parameters and return values
   - Write comprehensive docstrings for classes and methods
   - Include inline comments for complex logic

2. **Testing Requirements**
   - Write unit tests for all new functions
   - Include integration tests for new features
   - Maintain test coverage above 80%
   - Test error conditions and edge cases

3. **Documentation**
   - Update README.md for new features
   - Add docstrings to all public methods
   - Include usage examples in code
   - Document configuration changes

### Adding New Agents

```python
# Template for new agent implementation
from dataclasses import dataclass
from typing import Dict, Any, Optional
from agno.agent import Agent
from agno.models.gemini import Gemini

@dataclass
class NewAgentRequest:
    input_data: str
    context: Optional[Dict[str, Any]] = None

@dataclass
class NewAgentResult:
    output_data: str
    confidence: float
    metadata: Dict[str, Any]

class NewAgent:
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        self.model_name = model_name
        self.agent = Agent(
            model=Gemini(id=model_name),
            markdown=False
        )
    
    async def process(self, request: NewAgentRequest) -> NewAgentResult:
        """
        Process the agent request.
        
        Args:
            request: Input request with data and context
            
        Returns:
            Result with processed output and metadata
        """
        try:
            # Implementation logic here
            response = await self.agent.run(prompt)
            
            return NewAgentResult(
                output_data=response.content,
                confidence=0.95,
                metadata={"model": self.model_name}
            )
        except Exception as e:
            # Error handling
            return NewAgentResult(
                output_data="",
                confidence=0.0,
                metadata={"error": str(e)}
            )
```

---

## 📚 API Reference

### Authentication Endpoints

#### POST /auth/token
Authenticate user and obtain JWT token.

**Request:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

#### GET /auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "sub": "admin",
    "role": "admin",
    "region": "global",
    "permissions": ["read", "write", "query", "admin"]
}
```

### Text-to-SQL Endpoints

#### POST /api/sql
Convert natural language to SQL and execute query.

**Request:**
```json
{
    "question": "How many orders were placed last month?"
}
```

**Response:**
```json
{
    "sql": "SELECT COUNT(*) FROM orders WHERE order_date >= '2024-01-01'",
    "rows": [{"count": 1250}],
    "explanation": "Based on the data, there were 1,250 orders placed last month. This represents a typical volume for this time period."
}
```

### RAG Endpoints

#### POST /api/rag/query
Search documents and get AI-generated answers.

**Request:**
```json
{
    "question": "What is our return policy?"
}
```

**Response:**
```json
{
    "answer": "According to our return policy, customers can return items within 30 days of purchase for a full refund...",
    "sources": [
        {
            "text": "Return Policy: Items may be returned within 30 days...",
            "metadata": {"source": "policy_manual.pdf", "page": 15}
        }
    ]
}
```

#### POST /api/rag/ingest
Add documents to the knowledge base.

**Request:**
```json
{
    "document": "Company policy document content...",
    "metadata": {
        "source": "employee_handbook",
        "date": "2024-01-01",
        "version": "2.1"
    }
}
```

**Response:**
```json
{
    "status": "Document ingested successfully"
}
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Error:** `Connection refused` or `Could not connect to server`

**Solutions:**
- Verify PostgreSQL is running: `pg_ctl status`
- Check connection string in `.env` file
- Ensure database exists: `createdb syngen_ai`
- Verify user permissions

#### 2. Authentication Failures

**Error:** `Invalid authentication credentials`

**Solutions:**
- Check JWT_SECRET in environment variables
- Verify token hasn't expired
- Ensure proper Authorization header format: `Bearer <token>`

#### 3. Agent Initialization Errors

**Error:** `Failed to initialize agents`

**Solutions:**
- Verify all required dependencies are installed
- Check API keys for external services (Gemini)
- Ensure database schema is created
- Check Redis connectivity

#### 4. SQL Generation Issues

**Error:** `Unable to generate SQL` or poor query quality

**Solutions:**
- Verify database schema is loaded correctly
- Check if question is clear and specific
- Review few-shot examples for similar queries
- Ensure proper table relationships exist

### Debugging Tips

#### Enable Debug Logging
```env
LOG_LEVEL=DEBUG
```

#### Check System Health
```bash
curl http://localhost:8000/health
```

#### Monitor Request Processing
```python
# Add debug logging to see request flow
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Database Query Analysis
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM orders WHERE order_date > '2024-01-01';
```

---

## 📋 Changelog

### Version 1.0.0 (Current)

**Features:**
- Multi-agent architecture with specialized AI agents
- Comprehensive Text-to-SQL pipeline with security validation
- RAG system for document search and question answering
- JWT-based authentication and role-based access control
- Real-time query performance monitoring
- Automatic SQL error detection and fixing
- Natural language result explanation
- Comprehensive test suite

**Security:**
- SQL injection prevention
- Role-based table access controls
- Query cost analysis and limits
- Comprehensive audit logging

**Performance:**
- Redis caching for schema and queries
- Async database operations
- Connection pooling
- Query optimization

---

## 🙏 Acknowledgments

- **Agno Framework** - For the powerful agent orchestration capabilities
- **FastAPI** - For the robust and fast web framework
- **PostgreSQL** - For reliable database functionality
- **Redis** - For high-performance caching
- **SQLGlot** - For SQL parsing and validation

---

## 📞 Support

For questions, issues, or contributions:

1. **GitHub Issues**: Report bugs and feature requests
2. **Documentation**: Comprehensive README and inline comments
3. **Tests**: Extensive test suite for validation
4. **Code Review**: All changes should be reviewed

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ by the SynGen AI Team**

*Making enterprise data accessible through natural language interfaces with AI-powered intelligence and enterprise-grade security.*