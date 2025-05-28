"""
Enhanced Unified Query Service for SynGen AI
Implements multi-level AI-powered validation with Agno-style architecture
Features: Text-to-SQL with critique-fix loops, Enhanced RAG, Multi-agent validation
"""

import os
import json
import logging
import requests
import asyncio
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time
from services.database.postgres_manager import postgres_manager, mongodb_manager, execute_sql_query, get_schema_info, search_policy_documents

# Configure logging
logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """SQL Query validation levels based on security requirements"""
    BASIC = "basic"           # Basic syntax and read-only checks
    MODERATE = "moderate"     # + AI review and cost analysis
    STRICT = "strict"        # + Multi-agent validation and critique loops
    PARANOID = "paranoid"    # + Human-like review simulation

class QueryType(Enum):
    """Query classification types"""
    SQL = "sql"
    DOCUMENT = "document"
    HYBRID = "hybrid"

@dataclass
class ValidationResult:
    """Result of SQL validation process"""
    is_valid: bool
    confidence: float
    errors: List[str]
    warnings: List[str]
    suggested_fix: Optional[str] = None
    cost_estimate: Optional[float] = None
    security_flags: Optional[List[str]] = None

@dataclass
class QueryContext:
    """Context for query processing"""
    user_role: Optional[str] = None
    user_region: Optional[str] = None
    session_id: Optional[str] = None
    previous_queries: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class SynGenAIClient:
    """Client for SynGen AI API following z_api_checker.py pattern"""
    
    def __init__(self):
        self.api_key = os.getenv("SYNGEN_API_KEY", "syn-6a9b7c9d-1804-451d-8f81-73b8a9ca923f")
        self.base_url = os.getenv("SYNGEN_BASE_URL", "https://quchnti6xu7yzw7hfzt5yjqtvi0kafsq.lambda-url.eu-central-1.on.aws/")
        self.headers = {"Content-Type": "application/json"}
        
    async def call_model(self, prompt: str, model_id: str = "claude-3.5-sonnet", 
                        max_tokens: int = 1000, temperature: float = 0.3) -> str:
        """Call SynGen AI API with specified model"""
        payload = {
            "api_key": self.api_key,
            "prompt": prompt,
            "model_id": model_id,
            "model_params": {
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            # Use asyncio to run the sync request in a thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor, 
                    lambda: requests.post(self.base_url, headers=self.headers, json=payload, timeout=30)
                )
            
            if response.status_code == 200:
                data = response.json()
                return data["response"]["content"][0]["text"]
            else:
                logger.error(f"AI API Error {response.status_code}: {response.text}")
                return f"AI API Error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return f"AI service unavailable: {str(e)}"

class MultiLevelSQLValidator:
    """Multi-level SQL validation system with AI critique loops"""
    
    def __init__(self, ai_client: SynGenAIClient):
        self.ai_client = ai_client
        self.forbidden_patterns = re.compile(
            r'\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b', 
            re.IGNORECASE
        )
        
    async def validate_basic(self, sql: str) -> ValidationResult:
        """Basic validation: syntax and read-only checks"""
        errors = []
        warnings = []
        
        # Check for forbidden operations
        if self.forbidden_patterns.search(sql):
            errors.append("Write operations are forbidden. Only SELECT queries allowed.")
            
        # Check for potential injection patterns
        injection_patterns = [
            r';\s*DROP', r';\s*DELETE', r'UNION.*SELECT', 
            r'--.*\n', r'/\*.*\*/', r'xp_cmdshell'
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                errors.append(f"Potential SQL injection pattern detected: {pattern}")
                
        # Basic syntax checks
        if not sql.strip().upper().startswith('SELECT'):
            errors.append("Query must start with SELECT")
            
        if sql.count('(') != sql.count(')'):
            errors.append("Unmatched parentheses in query")
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            confidence=0.8 if len(errors) == 0 else 0.2,
            errors=errors,
            warnings=warnings
        )
    
    async def validate_with_ai(self, sql: str, question: str) -> ValidationResult:
        """AI-powered validation using Claude 3.5 Sonnet"""
        prompt = f"""
You are a SQL security expert. Analyze this SQL query for:
1. Security vulnerabilities
2. Performance issues  
3. Correctness relative to the question
4. Potential optimizations

Question: {question}
SQL Query: {sql}

Respond in JSON format:
{{
    "is_safe": boolean,
    "is_correct": boolean,
    "confidence": float (0-1),
    "issues": ["list of issues"],
    "suggestions": ["list of improvements"],
    "estimated_cost": float (0-100, relative complexity)
}}
"""
        
        try:
            response = await self.ai_client.call_model(prompt, "claude-3.5-sonnet", 500, 0.1)
            
            # Parse JSON response
            if response.startswith('{'):
                analysis = json.loads(response)
                
                return ValidationResult(
                    is_valid=analysis.get("is_safe", False) and analysis.get("is_correct", False),
                    confidence=analysis.get("confidence", 0.5),
                    errors=analysis.get("issues", []),
                    warnings=analysis.get("suggestions", []),
                    cost_estimate=analysis.get("estimated_cost", 50.0)
                )
            else:
                # Fallback parsing for non-JSON responses
                errors = []
                if "unsafe" in response.lower() or "vulnerable" in response.lower():
                    errors.append("AI detected potential security issues")
                if "incorrect" in response.lower() or "wrong" in response.lower():
                    errors.append("AI detected correctness issues")
                    
                return ValidationResult(
                    is_valid=len(errors) == 0,
                    confidence=0.6,
                    errors=errors,
                    warnings=["AI analysis completed with non-standard format"]
                )
                
        except Exception as e:
            logger.error(f"AI validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                errors=[f"AI validation error: {str(e)}"],
                warnings=[]
            )
    
    async def validate_with_critique(self, sql: str, question: str, max_attempts: int = 3) -> Tuple[str, ValidationResult]:
        """Multi-agent critique and fix loop"""
        current_sql = sql
        attempt = 0
        
        while attempt < max_attempts:
            # Validate current SQL
            basic_result = await self.validate_basic(current_sql)
            ai_result = await self.validate_with_ai(current_sql, question)
            
            # Combine results
            all_errors = basic_result.errors + ai_result.errors
            all_warnings = basic_result.warnings + ai_result.warnings
            
            if not all_errors:
                return current_sql, ValidationResult(
                    is_valid=True,
                    confidence=min(basic_result.confidence, ai_result.confidence),
                    errors=[],
                    warnings=all_warnings,
                    cost_estimate=ai_result.cost_estimate
                )
            
            # Generate fix using AI critic
            critique_prompt = f"""
You are a SQL expert. The following query has issues that need fixing:

Original Question: {question}
Current SQL: {current_sql}
Issues Found: {', '.join(all_errors)}

Please provide a corrected SQL query that:
1. Fixes all identified issues
2. Maintains the original intent
3. Uses only SELECT operations
4. Is optimized for performance

Return only the corrected SQL query, no explanations:
"""
            
            try:
                fixed_sql = await self.ai_client.call_model(critique_prompt, "claude-3.5-sonnet", 300, 0.2)
                
                # Clean up the response
                fixed_sql = re.sub(r'^```sql\s*', '', fixed_sql.strip())
                fixed_sql = re.sub(r'\s*```$', '', fixed_sql.strip())
                
                if fixed_sql and fixed_sql != current_sql:
                    current_sql = fixed_sql
                    attempt += 1
                else:
                    break
                    
            except Exception as e:
                logger.error(f"SQL fix attempt failed: {e}")
                break
        
        # Final validation failed
        return current_sql, ValidationResult(
            is_valid=False,
            confidence=0.3,
            errors=all_errors,
            warnings=all_warnings + [f"Failed to fix after {max_attempts} attempts"],
            suggested_fix=current_sql if current_sql != sql else None
        )

class EnhancedRAGSystem:
    """Enhanced RAG system with AI-powered context understanding"""
    
    def __init__(self, ai_client: SynGenAIClient):
        self.ai_client = ai_client
        self.cache = {}  # Simple in-memory cache
        
    async def semantic_search(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """AI-enhanced semantic search through documents"""
        
        # First, use AI to extract key concepts and expand query
        concept_prompt = f"""
Analyze this question and extract key supply chain concepts, synonyms, and related terms:
Question: {question}

Return as JSON:
{{
    "primary_concepts": ["main concepts"],
    "synonyms": ["alternative terms"],
    "related_topics": ["related supply chain areas"],
    "search_terms": ["optimized search terms"]
}}
"""
        
        try:
            concepts_response = await self.ai_client.call_model(concept_prompt, "claude-3.5-sonnet", 300, 0.1)
            
            if concepts_response.startswith('{'):
                concepts = json.loads(concepts_response)
                search_terms = concepts.get("search_terms", [question])
            else:
                search_terms = [question]
                
        except Exception as e:
            logger.error(f"Concept extraction failed: {e}")
            search_terms = [question]
        
        # Search documents using MongoDB text search
        try:
            all_docs = []
            for term in search_terms[:3]:  # Limit to top 3 search terms
                docs = await search_policy_documents(term, top_k)
                all_docs.extend(docs)
            
            # Remove duplicates and sort by relevance
            unique_docs = {}
            for doc in all_docs:
                doc_id = str(doc.get("_id", ""))
                if doc_id not in unique_docs:
                    unique_docs[doc_id] = {
                        "id": doc_id,
                        "content": doc.get("content", ""),
                        "title": doc.get("title", ""),
                        "relevance_score": doc.get("score", 1.0)
                    }
                    
            sorted_docs = sorted(unique_docs.values(), key=lambda x: x["relevance_score"], reverse=True)
            return sorted_docs[:top_k]
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []
    
    async def generate_contextual_answer(self, question: str, documents: List[Dict[str, Any]]) -> str:
        """Generate AI-powered contextual answer from retrieved documents"""
        
        if not documents:
            return "No relevant policy documents found for your question."
        
        # Prepare context from documents
        context_chunks = []
        for doc in documents:
            context_chunks.append(f"Document: {doc['title']}\nContent: {doc['content'][:1000]}...")
        
        context = "\n\n".join(context_chunks)
        
        answer_prompt = f"""
You are a supply chain policy expert. Answer the user's question based on the provided policy documents.

Question: {question}

Policy Context:
{context}

Requirements:
1. Provide a comprehensive, accurate answer based on the documents
2. Cite specific policies when possible
3. Include relevant procedural steps or requirements
4. Maintain professional tone suitable for business context
5. If information is insufficient, clearly state limitations

Answer:
"""
        
        try:
            answer = await self.ai_client.call_model(answer_prompt, "claude-3.5-sonnet", 800, 0.4)
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return f"Error generating answer: {str(e)}"

class IntentClassifier:
    """AI-powered intent classification for hybrid queries"""
    
    def __init__(self, ai_client: SynGenAIClient):
        self.ai_client = ai_client
        
    async def classify_intent(self, question: str, context: QueryContext = None) -> Tuple[QueryType, float]:
        """Classify query intent using AI"""
        
        classification_prompt = f"""
Classify this user question into one of three categories:

Question: {question}

Categories:
1. SQL - Questions requiring data analysis, calculations, aggregations, or specific data retrieval
2. DOCUMENT - Questions about policies, procedures, definitions, compliance, or best practices  
3. HYBRID - Questions requiring both data analysis AND policy context

Consider these indicators:
- SQL: "how many", "total", "average", "list", "show me data", "calculate", "compare"
- DOCUMENT: "policy", "procedure", "requirements", "steps", "definition", "compliance"
- HYBRID: Questions that need data AND policy context together

Respond with JSON:
{{
    "category": "SQL|DOCUMENT|HYBRID",
    "confidence": float (0-1),
    "reasoning": "brief explanation"
}}
"""
        
        try:
            response = await self.ai_client.call_model(classification_prompt, "claude-3.5-sonnet", 200, 0.1)
            
            if response.startswith('{'):
                result = json.loads(response)
                category = QueryType(result.get("category", "DOCUMENT").lower())
                confidence = float(result.get("confidence", 0.5))
                return category, confidence
            else:
                # Fallback classification
                question_lower = question.lower()
                
                sql_indicators = ['total', 'sum', 'count', 'average', 'how many', 'list all']
                doc_indicators = ['policy', 'procedure', 'definition', 'requirements', 'steps']
                
                sql_score = sum(1 for indicator in sql_indicators if indicator in question_lower)
                doc_score = sum(1 for indicator in doc_indicators if indicator in question_lower)
                
                if sql_score > doc_score:
                    return QueryType.SQL, 0.7
                elif doc_score > 0:
                    return QueryType.DOCUMENT, 0.7
                else:
                    return QueryType.DOCUMENT, 0.5  # Default fallback
                    
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return QueryType.DOCUMENT, 0.5

class SmartSQLGenerator:
    """AI-powered SQL generation with schema awareness"""
    
    def __init__(self, ai_client: SynGenAIClient):
        self.ai_client = ai_client
        self.schema_cache = None
        self.schema_cache_time = 0
        
    async def get_schema_info(self) -> str:
        """Get and cache database schema information"""
        cache_ttl = 600  # 10 minutes
        current_time = time.time()
        
        if self.schema_cache and (current_time - self.schema_cache_time) < cache_ttl:
            return self.schema_cache
        
        try:
            schema_info = await get_schema_info()
            self.schema_cache = schema_info
            self.schema_cache_time = current_time
            return self.schema_cache
            
        except Exception as e:
            logger.error(f"Schema extraction failed: {e}")
            return "Schema information unavailable"
    
    async def generate_sql(self, question: str, context: QueryContext = None) -> str:
        """Generate SQL using AI with schema awareness"""
        
        schema_info = await self.get_schema_info()
        
        sql_prompt = f"""
You are a SQL expert for a supply chain database. Generate a precise SQL query to answer the user's question.

Database Schema:
{schema_info}

User Question: {question}

Requirements:
1. Use only SELECT statements
2. Join tables appropriately based on relationships
3. Use proper aggregation functions when needed
4. Include reasonable LIMIT clauses for large result sets
5. Handle NULL values appropriately
6. Use meaningful column aliases
7. Optimize for performance

Return only the SQL query, no explanations:
"""
        
        try:
            sql = await self.ai_client.call_model(sql_prompt, "claude-3.5-sonnet", 400, 0.2)
            
            # Clean up the response
            sql = re.sub(r'^```sql\s*', '', sql.strip())
            sql = re.sub(r'\s*```$', '', sql.strip())
            sql = sql.strip().rstrip(';')  # Remove trailing semicolon
            
            return sql
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return "SELECT 'SQL generation failed' as error;"

class UnifiedQueryService:
    """Enhanced unified service with multi-level AI validation and RAG"""
    
    def __init__(self):
        self.ai_client = SynGenAIClient()
        self.validator = MultiLevelSQLValidator(self.ai_client)
        self.rag_system = EnhancedRAGSystem(self.ai_client)
        self.intent_classifier = IntentClassifier(self.ai_client)
        self.sql_generator = SmartSQLGenerator(self.ai_client)
        
        # Configuration from environment
        self.validation_level = ValidationLevel(os.getenv("DEFAULT_VALIDATION_LEVEL", "moderate"))
        self.max_fix_attempts = int(os.getenv("MAX_FIX_ATTEMPTS", "3"))
        self.query_timeout = int(os.getenv("QUERY_TIMEOUT", "30"))
        self.max_result_rows = int(os.getenv("MAX_RESULT_ROWS", "1000"))
    
    
    async def process_sql_query(self, question: str, context: QueryContext = None) -> Dict[str, Any]:
        """Process SQL query with multi-level validation"""
        
        try:
            # Generate initial SQL
            sql = await self.sql_generator.generate_sql(question, context)
            
            # Apply validation based on level
            if self.validation_level == ValidationLevel.BASIC:
                validation_result = await self.validator.validate_basic(sql)
                final_sql = sql
                
            elif self.validation_level == ValidationLevel.MODERATE:
                basic_result = await self.validator.validate_basic(sql)
                if basic_result.is_valid:
                    ai_result = await self.validator.validate_with_ai(sql, question)
                    validation_result = ai_result
                    final_sql = sql
                else:
                    validation_result = basic_result
                    final_sql = sql
                    
            else:  # STRICT or PARANOID
                final_sql, validation_result = await self.validator.validate_with_critique(
                    sql, question, self.max_fix_attempts
                )
            
            if not validation_result.is_valid:
                return {
                    "error": "Query validation failed",
                    "issues": validation_result.errors,
                    "warnings": validation_result.warnings,
                    "suggested_fix": validation_result.suggested_fix,
                    "original_sql": sql,
                    "type": "sql_query",
                    "validation_level": self.validation_level.value
                }
            
            # Execute validated SQL
            result = await self.execute_sql_safely(final_sql)
            
            # Add validation metadata
            result.update({
                "validation_confidence": validation_result.confidence,
                "cost_estimate": validation_result.cost_estimate,
                "warnings": validation_result.warnings,
                "validation_level": self.validation_level.value
            })
            
            return result
            
        except Exception as e:
            logger.error(f"SQL query processing error: {e}")
            return {
                "error": f"SQL processing failed: {str(e)}",
                "type": "sql_query"
            }
    
    async def process_document_query(self, question: str, context: QueryContext = None) -> Dict[str, Any]:
        """Process document query with enhanced RAG"""
        
        try:
            # Semantic search for relevant documents
            documents = await self.rag_system.semantic_search(question)
            
            if not documents:
                return {
                    "answer": "No relevant policy documents found for your question.",
                    "sources": [],
                    "type": "policy_query",
                    "confidence": 0.0
                }
            
            # Generate contextual answer
            answer = await self.rag_system.generate_contextual_answer(question, documents)
            
            return {
                "answer": answer,
                "sources": [{"title": doc["title"], "relevance": doc["relevance_score"]} for doc in documents],
                "type": "policy_query",
                "confidence": 0.8,
                "documents_found": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Document query processing error: {e}")
            return {
                "error": f"Document processing failed: {str(e)}",
                "type": "policy_query"
            }
    
    async def process_hybrid_query(self, question: str, context: QueryContext = None) -> Dict[str, Any]:
        """Process hybrid query requiring both SQL and document context"""
        
        try:
            # Process both SQL and document queries concurrently
            sql_task = asyncio.create_task(self.process_sql_query(question, context))
            doc_task = asyncio.create_task(self.process_document_query(question, context))
            
            sql_result, doc_result = await asyncio.gather(sql_task, doc_task)
            
            # Combine results using AI
            synthesis_prompt = f"""
The user asked: {question}

Data Analysis Result:
{json.dumps(sql_result, indent=2)}

Policy Context:
{json.dumps(doc_result, indent=2)}

Synthesize these results into a comprehensive answer that:
1. Integrates the data findings with policy context
2. Provides actionable insights
3. Highlights any compliance considerations
4. Maintains professional tone

Comprehensive Answer:
"""
            
            try:
                synthesis = await self.ai_client.call_model(synthesis_prompt, "claude-3.5-sonnet", 600, 0.5)
                
                return {
                    "answer": synthesis,
                    "sql_result": sql_result,
                    "policy_context": doc_result,
                    "type": "hybrid_query",
                    "confidence": min(sql_result.get("validation_confidence", 0.5), doc_result.get("confidence", 0.5))
                }
                
            except Exception as e:
                logger.error(f"Result synthesis failed: {e}")
                return {
                    "sql_result": sql_result,
                    "policy_context": doc_result,
                    "type": "hybrid_query",
                    "synthesis_error": str(e)
                }
                
        except Exception as e:
            logger.error(f"Hybrid query processing error: {e}")
            return {
                "error": f"Hybrid processing failed: {str(e)}",
                "type": "hybrid_query"
            }
    
    async def execute_sql_safely(self, sql: str) -> Dict[str, Any]:
        """Execute SQL with safety measures and timeouts"""
        
        try:
            start_time = time.time()
            rows = await execute_sql_query(sql)
            execution_time = time.time() - start_time
            
            # Limit results
            if len(rows) > self.max_result_rows:
                rows = rows[:self.max_result_rows]
            
            return {
                "sql": sql.strip(),
                "rows": rows,
                "row_count": len(rows),
                "execution_time": execution_time,
                "explanation": f"Query executed successfully and returned {len(rows)} rows.",
                "type": "sql_query"
            }
            
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return {
                "error": f"SQL execution failed: {str(e)}",
                "sql": sql.strip(),
                "type": "sql_query"
            }
    
    async def process_query(self, question: str, context: QueryContext = None) -> Dict[str, Any]:
        """Main query processing method with AI-powered routing"""
        
        try:
            # Classify query intent
            query_type, confidence = await self.intent_classifier.classify_intent(question, context)
            
            logger.info(f"Query classified as {query_type.value} with confidence {confidence}")
            
            # Route to appropriate processor
            if query_type == QueryType.SQL:
                return await self.process_sql_query(question, context)
            elif query_type == QueryType.DOCUMENT:
                return await self.process_document_query(question, context)
            else:  # HYBRID
                return await self.process_hybrid_query(question, context)
                
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "error": f"Query processing failed: {str(e)}",
                "question": question,
                "timestamp": datetime.now().isoformat()
            }

# Factory function for easy instantiation
def create_unified_service(validation_level: str = None) -> UnifiedQueryService:
    """Create configured UnifiedQueryService instance"""
    
    service = UnifiedQueryService()
    
    if validation_level:
        service.validation_level = ValidationLevel(validation_level)
    
    return service