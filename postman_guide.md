# SynGen AI - Postman Testing Guide

This guide provides step-by-step instructions for testing all SynGen AI features using Postman.

## =€ Getting Started

### Prerequisites
1. **Start the Application**
   ```bash
   cd /mnt/d/Coding/SynGen-ai/Backend
   uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Base URL**: `http://localhost:8000`

3. **Postman Setup**
   - Create a new Postman collection called "SynGen AI"
   - Set up environment variables:
     - `base_url`: `http://localhost:8000`
     - `access_token`: (will be set after authentication)

---

## =Ë API Endpoints Overview

### Core Features
-  **Health Check & System Info**
- = **Authentication & User Management**
- > **Text-to-SQL Pipeline**
- =Ú **RAG Document Search**
- =Ê **Analytics & Monitoring**

---

## 1. Health Check & System Status

### 1.1 Root Endpoint - Welcome Message
**Request:**
```http
GET {{base_url}}/
```
**Expected Response:**
```json
{
  "message": "Welcome to SynGen AI - Advanced Supply Chain Analytics Platform",
  "version": "1.0.0",
  "status": "operational",
  "timestamp": "2024-01-15T10:30:45.123456",
  "features": ["text-to-sql", "rag-search", "analytics"]
}
```

### 1.2 Health Check - System Status
**Request:**
```http
GET {{base_url}}/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456",
  "services": {
    "database": "connected",
    "ai_agents": "initialized",
    "cache": "operational",
    "storage": "available"
  },
  "version": "1.0.0"
}
```

### 1.3 API Documentation - Swagger UI
**Request:**
```http
GET {{base_url}}/docs
```
**Expected:** Interactive Swagger UI documentation interface

---

## 2. Authentication System

### 2.1 User Registration
**Request:**
```http
POST {{base_url}}/auth/register
Content-Type: application/json
```
**Body:**
```json
{
  "username": "testuser",
  "email": "test@syngen.ai",
  "password": "SecurePass123!",
  "full_name": "Test User",
  "role": "analyst",
  "region": "north_america"
}
```
**Expected Response:**
```json
{
  "message": "User registered successfully",
  "user_id": 1,
  "username": "testuser",
  "email": "test@syngen.ai",
  "role": "analyst"
}
```

### 2.2 Login & Get Access Token
**Request:**
```http
POST {{base_url}}/auth/token
Content-Type: application/x-www-form-urlencoded
```
**Body (form-data):**
```
username=testuser
password=SecurePass123!
```
**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**=Ý Important:** Copy the `access_token` and set it as `{{access_token}}` in your Postman environment.

### 2.3 Get Current User Profile
**Request:**
```http
GET {{base_url}}/auth/me
Authorization: Bearer {{access_token}}
```
**Expected Response:**
```json
{
  "user_id": 1,
  "username": "testuser",
  "email": "test@syngen.ai",
  "full_name": "Test User",
  "role": "analyst",
  "region": "north_america",
  "is_active": true,
  "permissions": ["read_data", "generate_reports"],
  "created_at": "2024-01-15T10:30:45.123456"
}
```

---

## 3. Text-to-SQL Features >

### 3.1 Simple Customer Query
**Request:**
```http
POST {{base_url}}/api/sql
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "Show me all customers from New York",
  "context": {
    "user_role": "analyst",
    "region": "north_america"
  }
}
```
**Expected Response:**
```json
{
  "request_id": "req_123456",
  "intent": "sql_query",
  "confidence": 0.95,
  "sql": "SELECT * FROM customers WHERE city = 'New York'",
  "explanation": "This query retrieves all customer records where the city is New York.",
  "data": [
    {
      "customer_id": 1001,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@email.com",
      "city": "New York",
      "state": "NY"
    }
  ],
  "metadata": {
    "row_count": 15,
    "execution_time": 0.15,
    "performance_score": 8.5
  }
}
```

### 3.2 Sales Aggregation Query
**Request:**
```http
POST {{base_url}}/api/sql
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "What are the total sales by region this year?",
  "context": {
    "user_role": "analyst",
    "region": "global"
  }
}
```
**Expected Response:**
```json
{
  "request_id": "req_123457",
  "intent": "sql_query",
  "sql": "SELECT order_region, SUM(sales) as total_sales FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2024 GROUP BY order_region ORDER BY total_sales DESC",
  "explanation": "This query calculates total sales by region for the current year.",
  "data": [
    {
      "order_region": "North America",
      "total_sales": 1250000.50
    },
    {
      "order_region": "Europe", 
      "total_sales": 980000.25
    }
  ],
  "insights": [
    "North America leads with $1.25M in sales",
    "Strong performance across all regions"
  ],
  "suggested_visualizations": ["bar_chart", "pie_chart"]
}
```

### 3.3 Complex Join Query - Customer Orders
**Request:**
```http
POST {{base_url}}/api/sql
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "Show me top 5 customers by total order value with their details",
  "context": {
    "user_role": "manager",
    "limit": 5
  }
}
```

### 3.4 Time-Series Analysis
**Request:**
```http
POST {{base_url}}/api/sql
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "Show monthly sales trends for the last 6 months",
  "context": {
    "user_role": "analyst",
    "include_forecasting": true
  }
}
```

### 3.5 Product Performance Query
**Request:**
```http
POST {{base_url}}/api/sql
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "Which products have the highest profit margins?",
  "context": {
    "user_role": "product_manager",
    "department": "electronics"
  }
}
```

---

## 4. RAG Document Search =Ú

### 4.1 Inventory Policy Search
**Request:**
```http
POST {{base_url}}/api/rag/query
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "What is our inventory management policy?",
  "context": {
    "document_types": ["policy"],
    "max_results": 5,
    "include_summary": true
  }
}
```
**Expected Response:**
```json
{
  "request_id": "rag_123456",
  "intent": "document_search",
  "query": "What is our inventory management policy?",
  "results": [
    {
      "document_id": "policy_inv_001",
      "title": "DataCo Global Warehouse and Storage Policy",
      "content": "Our inventory management policy ensures optimal stock levels through automated reorder points...",
      "relevance_score": 0.95,
      "source": "DataCo Global Warehouse and Storage Policy.pdf",
      "section": "Section 2: Inventory Control",
      "page": 5
    }
  ],
  "summary": "The inventory management policy focuses on maintaining optimal stock levels through automated reorder points and regular audits.",
  "related_topics": ["warehouse_operations", "supply_chain"],
  "confidence": 0.88
}
```

### 4.2 Supplier Compliance Search
**Request:**
```http
POST {{base_url}}/api/rag/query
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "What are the requirements for supplier selection and evaluation?",
  "context": {
    "document_types": ["policy", "procedure"],
    "department": "procurement"
  }
}
```

### 4.3 Quality Assurance Guidelines
**Request:**
```http
POST {{base_url}}/api/rag/query
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "What are our quality control procedures for incoming shipments?",
  "context": {
    "document_types": ["policy"],
    "region": "global"
  }
}
```

### 4.4 Sustainability Policies
**Request:**
```http
POST {{base_url}}/api/rag/query
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "What are our environmental sustainability commitments?",
  "context": {
    "document_types": ["policy"],
    "categories": ["sustainability", "environment"]
  }
}
```

---

## 5. User Management & Admin

### 5.1 List All Users (Admin Only)
**Request:**
```http
GET {{base_url}}/api/users?page=1&limit=10
Authorization: Bearer {{access_token}}
```
**Expected Response:**
```json
{
  "users": [
    {
      "user_id": 1,
      "username": "testuser",
      "email": "test@syngen.ai",
      "role": "analyst",
      "is_active": true,
      "last_login": "2024-01-15T10:30:45.123456"
    }
  ],
  "pagination": {
    "total": 25,
    "page": 1,
    "per_page": 10,
    "pages": 3
  }
}
```

### 5.2 Update User Profile
**Request:**
```http
PUT {{base_url}}/api/users/me
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "full_name": "Updated Test User",
  "email": "updated@syngen.ai"
}
```

### 5.3 Change Password
**Request:**
```http
POST {{base_url}}/auth/change-password
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "current_password": "SecurePass123!",
  "new_password": "NewSecurePass456!"
}
```

---

## 6. System Monitoring & Analytics =Ê

### 6.1 Query Performance Statistics
**Request:**
```http
GET {{base_url}}/api/stats/queries
Authorization: Bearer {{access_token}}
```
**Expected Response:**
```json
{
  "total_queries": 1547,
  "successful_queries": 1502,
  "failed_queries": 45,
  "success_rate": 0.97,
  "average_response_time": 0.25,
  "most_common_intents": [
    {"intent": "sql_query", "count": 1200, "percentage": 78},
    {"intent": "document_search", "count": 302, "percentage": 20}
  ],
  "performance_trends": {
    "last_24h": "improving",
    "avg_response_time": 0.23
  }
}
```

### 6.2 System Health & Performance
**Request:**
```http
GET {{base_url}}/api/stats/system
Authorization: Bearer {{access_token}}
```
**Expected Response:**
```json
{
  "system_health": "healthy",
  "uptime": "72h 15m",
  "response_times": {
    "p50": 0.15,
    "p95": 0.45,
    "p99": 0.80
  },
  "active_users": 12,
  "cache_hit_rate": 0.85,
  "database_connections": {
    "postgresql": "healthy",
    "mongodb": "healthy"
  }
}
```

### 6.3 User Activity Analytics
**Request:**
```http
GET {{base_url}}/api/stats/users
Authorization: Bearer {{access_token}}
```

---

## 7. Error Handling & Edge Cases  

### 7.1 Invalid SQL Attempt (Security Test)
**Request:**
```http
POST {{base_url}}/api/sql
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "query": "DROP TABLE customers; DELETE FROM orders;",
  "context": {}
}
```
**Expected Response:**
```json
{
  "error": "Security violation detected",
  "error_code": "SQL_SECURITY_ERROR",
  "message": "Dangerous SQL operations are not permitted",
  "details": "DROP and DELETE operations are blocked for security",
  "suggestions": [
    "Use SELECT queries to retrieve data",
    "Contact administrator for data modifications"
  ],
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### 7.2 Unauthorized Access Test
**Request:**
```http
GET {{base_url}}/api/admin/system
Authorization: Bearer invalid_token_here
```
**Expected Response:**
```json
{
  "detail": "Could not validate credentials",
  "error_code": "INVALID_TOKEN",
  "status_code": 401
}
```

### 7.3 Rate Limiting Test
**Test:** Make 50+ rapid requests to any endpoint
**Expected Response:**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please slow down.",
  "retry_after": 60,
  "limit": "100 requests per minute"
}
```

### 7.4 Malformed Request Test
**Request:**
```http
POST {{base_url}}/api/sql
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body:**
```json
{
  "invalid_field": "This should fail validation"
}
```
**Expected Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "error_code": "VALIDATION_ERROR"
}
```

---

## >ê Complete Testing Scenarios

### Scenario 1: Business Analyst Daily Workflow
1. **Login**: `POST /auth/token`
2. **Check System**: `GET /health`
3. **Customer Analysis**: `POST /api/sql` - "Show customer distribution by region"
4. **Sales Trends**: `POST /api/sql` - "Monthly sales for last quarter"
5. **Policy Check**: `POST /api/rag/query` - "KPI measurement policies"
6. **Performance**: `GET /api/stats/queries`

### Scenario 2: Supply Chain Manager Operations
1. **Authentication**: Login as manager
2. **Inventory Status**: `POST /api/sql` - "Current inventory levels by category"
3. **Supplier Performance**: `POST /api/sql` - "Delivery performance by supplier"
4. **Policy Review**: `POST /api/rag/query` - "Supplier evaluation criteria"
5. **Compliance Check**: `POST /api/rag/query` - "Trade compliance requirements"

### Scenario 3: Executive Dashboard Access
1. **Secure Login**: Executive credentials
2. **High-Level Metrics**: `POST /api/sql` - "Revenue and profit summary"
3. **Strategic Insights**: `POST /api/rag/query` - "Strategic planning policies"
4. **System Overview**: `GET /api/stats/system`
5. **User Activity**: `GET /api/stats/users`

---

## =' Troubleshooting Guide

### Common Issues & Solutions

| Issue | Status Code | Solution |
|-------|-------------|----------|
| **Invalid Token** | 401 | Re-authenticate and get new token |
| **Missing Fields** | 422 | Check required fields in request body |
| **Rate Limited** | 429 | Wait for rate limit reset |
| **Server Error** | 500 | Check logs, verify database connection |
| **Not Found** | 404 | Verify endpoint URL and method |

### Debug Endpoints (Development Only)
- **System Logs**: `GET /api/debug/logs`
- **Database Schema**: `GET /api/debug/schema`
- **Agent Status**: `GET /api/debug/agents`
- **Configuration**: `GET /api/debug/config`

### Performance Benchmarks
- ¡ **Authentication**: < 0.5 seconds
- > **SQL Generation**: < 2 seconds
- =Ú **Document Search**: < 1 second
- =Ê **Simple Queries**: < 1 second
- = **Complex Queries**: < 5 seconds

---

##  Success Validation Checklist

Use this checklist to verify your SynGen AI implementation:

- [ ] **System Health**: All health endpoints return "healthy"
- [ ] **Authentication**: Login flow works, tokens are valid
- [ ] **SQL Generation**: Natural language converts to valid SQL
- [ ] **Data Retrieval**: Queries return expected data format
- [ ] **Document Search**: RAG returns relevant policy content
- [ ] **Security**: Invalid operations are properly blocked
- [ ] **Error Handling**: Errors return helpful messages
- [ ] **Performance**: Response times meet benchmarks
- [ ] **Authorization**: Role-based access controls work
- [ ] **Monitoring**: Statistics and analytics are accurate

---

## =È Advanced Testing

### Load Testing
Use tools like Apache JMeter or Artillery to test:
- Concurrent user sessions
- High-volume query processing
- System performance under load

### Security Testing
- SQL injection attempts
- Authentication bypass tests
- Rate limiting validation
- Access control verification

### Integration Testing
- End-to-end user workflows
- Cross-service communication
- Database connectivity
- External API integrations

---

**<¯ Pro Tips:**
- Use Postman environments for different deployment stages (dev, staging, production)
- Set up automated test suites using Newman (Postman CLI)
- Monitor response times and set alerts for performance degradation
- Create comprehensive test collections for regression testing
- Document any custom configurations or environment-specific settings

---

**<Æ Expected Results:** A fully functional SynGen AI platform that converts natural language to SQL, searches policy documents intelligently, and provides comprehensive analytics for supply chain management.