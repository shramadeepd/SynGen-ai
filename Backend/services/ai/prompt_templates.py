"""
Comprehensive Prompt Templates for SynGen AI Agentic System
Production-ready prompts for different scenarios and use cases
Based on idea.txt guidelines and validation patterns
"""

from typing import Dict, Any, List
from enum import Enum

class PromptType(Enum):
    """Types of prompts in the system"""
    SQL_GENERATION = "sql_generation"
    SQL_VALIDATION = "sql_validation"
    SQL_OPTIMIZATION = "sql_optimization"
    RAG_SYNTHESIS = "rag_synthesis"
    INTENT_CLASSIFICATION = "intent_classification"
    RESULT_EXPLANATION = "result_explanation"
    ERROR_DIAGNOSIS = "error_diagnosis"
    SECURITY_ANALYSIS = "security_analysis"

class PromptTemplates:
    """Comprehensive collection of production-ready prompt templates"""
    
    @staticmethod
    def get_sql_generation_prompt(question: str, schema_info: str, examples: List[Dict] = None) -> str:
        """
        Advanced SQL generation prompt following idea.txt guidelines
        """
        
        examples_section = ""
        if examples:
            examples_section = "\n### Examples:\n"
            for i, example in enumerate(examples[:3]):  # Limit to 3 examples
                examples_section += f"Q: {example.get('question', '')}\nA: {example.get('sql', '')}\n\n"
        
        return f"""### Instructions:
Your task is to convert a question into a SQL query, given a database schema.
Adhere to these rules:
- **Deliberately go through the question and database schema word by word** to appropriately answer the question
- **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- When creating a ratio, always cast the numerator as float
- Use only SELECT statements - no INSERT, UPDATE, DELETE, DROP, or ALTER operations
- Add appropriate WHERE clauses to filter out invalid data (e.g., canceled orders)
- Use proper JOINs based on table relationships
- Include LIMIT clauses for large result sets (max 1000 rows)
- Handle NULL values appropriately with COALESCE or IS NOT NULL checks
- Use meaningful column aliases for better readability

### Database Schema:
{schema_info}

{examples_section}

### Input:
Generate a SQL query that answers the question: `{question}`

### Response:
Based on your instructions, here is the SQL query I have generated to answer the question `{question}`:

```sql"""

    @staticmethod
    def get_sql_validation_prompt(sql: str, question: str, schema_info: str = None) -> str:
        """
        SQL validation prompt with comprehensive security and correctness checks
        """
        
        schema_section = ""
        if schema_info:
            schema_section = f"\n### Database Schema:\n{schema_info}"
        
        return f"""### SQL Security and Correctness Analysis

You are a SQL security expert. Analyze this SQL query for:
1. **Security vulnerabilities** (SQL injection, unauthorized operations)
2. **Performance issues** (missing indexes, cartesian products, inefficient joins)
3. **Correctness relative to the question** (does it answer what was asked?)
4. **Best practices compliance** (proper aliasing, null handling, etc.)

### Original Question: 
{question}

### SQL Query to Analyze:
```sql
{sql}
```
{schema_section}

### Analysis Requirements:
- Check for forbidden operations (INSERT, UPDATE, DELETE, DROP, ALTER, etc.)
- Detect potential injection patterns (UNION attacks, comment injection, etc.)
- Verify proper table relationships and JOIN conditions
- Assess query complexity and performance implications
- Validate that the query actually answers the question asked

### Response Format (JSON):
{{
    "is_safe": boolean,
    "is_correct": boolean,
    "confidence": float (0-1),
    "security_issues": ["list of security concerns"],
    "performance_issues": ["list of performance concerns"],
    "correctness_issues": ["list of correctness concerns"],
    "suggestions": ["list of improvements"],
    "estimated_cost": float (0-100, relative complexity),
    "risk_level": "low|medium|high"
}}"""

    @staticmethod
    def get_sql_optimization_prompt(sql: str, performance_issues: List[str]) -> str:
        """
        SQL optimization prompt for improving query performance
        """
        
        issues_section = ""
        if performance_issues:
            issues_section = f"\n### Identified Issues:\n" + "\n".join(f"- {issue}" for issue in performance_issues)
        
        return f"""### SQL Query Optimization Task

You are a database performance expert. Optimize this SQL query while maintaining its correctness and intent.

### Original SQL Query:
```sql
{sql}
```
{issues_section}

### Optimization Guidelines:
1. **Maintain query correctness** - the optimized query must return the same logical results
2. **Improve performance** - reduce execution time and resource usage
3. **Follow best practices** - proper indexing hints, efficient joins, etc.
4. **Preserve readability** - keep the query maintainable

### Common Optimizations to Consider:
- Add appropriate LIMIT clauses
- Optimize JOIN order and conditions
- Use EXISTS instead of IN for subqueries
- Add proper WHERE clause filtering
- Use appropriate aggregate functions
- Consider index utilization

### Response:
Provide the optimized SQL query with brief explanation of changes:

**Optimized Query:**
```sql"""

    @staticmethod
    def get_rag_synthesis_prompt(question: str, documents: List[Dict[str, Any]], context: str = None) -> str:
        """
        RAG synthesis prompt for generating comprehensive policy answers
        """
        
        context_section = ""
        if context:
            context_section = f"\n### Additional Context:\n{context}"
        
        documents_section = ""
        if documents:
            documents_section = "\n### Policy Documents:\n"
            for i, doc in enumerate(documents[:5]):  # Limit to 5 documents
                title = doc.get('title', f'Document {i+1}')
                content = doc.get('content', '')[:1000] + '...' if len(doc.get('content', '')) > 1000 else doc.get('content', '')
                documents_section += f"\n**{title}:**\n{content}\n"
        
        return f"""### Supply Chain Policy Expert Assistant

You are a supply chain policy expert with deep knowledge of DataCo Global's policies and procedures. Answer the user's question based on the provided policy documents.

### User Question:
{question}
{documents_section}
{context_section}

### Response Requirements:
1. **Provide a comprehensive, accurate answer** based strictly on the policy documents
2. **Cite specific policies** when possible (mention policy names and sections)
3. **Include relevant procedural steps** or requirements in numbered/bulleted format
4. **Maintain professional tone** suitable for business context
5. **Be specific and actionable** - avoid vague generalities
6. **If information is insufficient**, clearly state limitations and suggest where to find more information
7. **Structure your response** with clear sections if the question has multiple parts

### Professional Answer:"""

    @staticmethod
    def get_intent_classification_prompt(question: str, context: Dict[str, Any] = None) -> str:
        """
        Intent classification prompt for routing queries appropriately
        """
        
        context_section = ""
        if context:
            user_role = context.get('user_role', 'unknown')
            user_region = context.get('user_region', 'unknown')
            context_section = f"\n### User Context:\n- Role: {user_role}\n- Region: {user_region}"
        
        return f"""### Query Intent Classification

Classify this user question into one of three categories for optimal processing:

### User Question:
"{question}"
{context_section}

### Categories:

**1. SQL** - Questions requiring data analysis, calculations, aggregations, or specific data retrieval
Examples: "total sales", "top customers", "average time", "count of orders", "distribution analysis"

**2. DOCUMENT** - Questions about policies, procedures, definitions, compliance, or best practices
Examples: "policy requirements", "procedure steps", "compliance standards", "definitions", "best practices"

**3. HYBRID** - Questions requiring both data analysis AND policy context together
Examples: "which suppliers don't meet our policy requirements", "items that qualify as X according to our policy"

### Classification Indicators:
- **SQL Keywords**: how many, total, sum, count, average, list, show me data, calculate, compare, highest, lowest
- **DOCUMENT Keywords**: policy, procedure, requirements, steps, definition, compliance, according to, standards, framework
- **HYBRID Keywords**: based on our policy, meet our requirements, qualify as, comply with our standards, exceed our thresholds

### Response (JSON):
{{
    "category": "SQL|DOCUMENT|HYBRID",
    "confidence": float (0-1),
    "reasoning": "brief explanation of classification decision",
    "suggested_approach": "recommended processing strategy",
    "complexity": "low|medium|high"
}}"""

    @staticmethod
    def get_result_explanation_prompt(query: str, results: Dict[str, Any], query_type: str) -> str:
        """
        Result explanation prompt for generating user-friendly explanations
        """
        
        results_summary = ""
        if query_type == "sql_query" and "rows" in results:
            row_count = len(results["rows"])
            if row_count > 0:
                sample_data = str(results["rows"][:3])  # Show first 3 rows
                results_summary = f"Returned {row_count} rows. Sample data: {sample_data}"
            else:
                results_summary = "No data found matching the criteria"
        elif query_type == "policy_query" and "answer" in results:
            answer_length = len(results["answer"])
            sources_count = len(results.get("sources", []))
            results_summary = f"Generated policy answer ({answer_length} characters) from {sources_count} sources"
        
        return f"""### Query Result Explanation

Generate a clear, business-friendly explanation of these query results for supply chain stakeholders.

### Original Query:
"{query}"

### Query Type: {query_type}

### Results Summary:
{results_summary}

### Full Results:
{str(results)[:2000]}...

### Explanation Requirements:
1. **Summarize the key findings** in plain business language
2. **Highlight important insights** or trends if applicable
3. **Provide context** for the numbers or information presented
4. **Suggest potential actions** or implications if relevant
5. **Keep it concise** but informative (2-4 sentences)
6. **Use supply chain terminology** appropriately

### Business-Friendly Explanation:"""

    @staticmethod
    def get_error_diagnosis_prompt(error: str, query: str, context: Dict[str, Any] = None) -> str:
        """
        Error diagnosis prompt for providing helpful error resolution
        """
        
        context_section = ""
        if context:
            context_section = f"\n### Context:\n{str(context)}"
        
        return f"""### Error Diagnosis and Resolution

You are a technical support expert helping users resolve query errors in the SynGen AI system.

### Original Query:
"{query}"

### Error Encountered:
{error}
{context_section}

### Diagnosis Requirements:
1. **Identify the root cause** of the error
2. **Explain in user-friendly terms** what went wrong
3. **Provide specific steps** to resolve the issue
4. **Suggest alternative approaches** if applicable
5. **Include prevention tips** to avoid similar errors

### Error Categories to Consider:
- SQL syntax errors
- Database connection issues
- Permission/security restrictions
- Data type mismatches
- Missing or invalid table/column references
- Query timeout or performance issues
- AI service limitations or quotas

### Response Format:
**Problem:** [Clear description of what went wrong]

**Cause:** [Root cause explanation]

**Solution:** [Step-by-step resolution]

**Prevention:** [Tips to avoid this error in the future]

**Alternative:** [If applicable, suggest different approach]"""

    @staticmethod
    def get_security_analysis_prompt(query: str, user_context: Dict[str, Any] = None) -> str:
        """
        Security analysis prompt for evaluating query safety
        """
        
        user_section = ""
        if user_context:
            role = user_context.get('role', 'unknown')
            region = user_context.get('region', 'unknown')
            permissions = user_context.get('permissions', [])
            user_section = f"\n### User Context:\n- Role: {role}\n- Region: {region}\n- Permissions: {permissions}"
        
        return f"""### Security Analysis for Query

Perform a comprehensive security analysis of this query request to ensure it complies with enterprise security policies.

### Query to Analyze:
"{query}"
{user_section}

### Security Analysis Framework:

**1. Access Control:**
- Does the user have permission to access requested data?
- Are there regional restrictions that apply?
- Does the query attempt to access sensitive information?

**2. Data Privacy:**
- Could the query expose PII or confidential business data?
- Are there data masking requirements?
- Does it comply with data governance policies?

**3. Injection Risks:**
- Are there potential SQL injection patterns?
- Could this be used for system reconnaissance?
- Are there attempts to access system metadata?

**4. Business Logic:**
- Is this a legitimate business use case?
- Could the query be used for competitive intelligence gathering?
- Are there rate limiting concerns?

### Security Assessment (JSON):
{{
    "security_level": "low|medium|high|critical",
    "access_approved": boolean,
    "risk_factors": ["list of identified risks"],
    "required_mitigations": ["list of required security measures"],
    "data_classification": "public|internal|confidential|restricted",
    "audit_required": boolean,
    "recommendations": ["list of security recommendations"]
}}"""

    @staticmethod
    def get_hybrid_synthesis_prompt(sql_result: Dict[str, Any], policy_result: Dict[str, Any], question: str) -> str:
        """
        Hybrid synthesis prompt for combining SQL and policy results
        """
        
        return f"""### Hybrid Query Result Synthesis

You are a supply chain analyst combining data analysis with policy guidance to provide comprehensive business insights.

### Original Question:
"{question}"

### Data Analysis Results:
{str(sql_result)[:1500]}...

### Policy Context:
{str(policy_result)[:1500]}...

### Synthesis Requirements:
1. **Integrate data findings with policy context** seamlessly
2. **Provide actionable business insights** that combine both perspectives
3. **Highlight compliance considerations** based on the data
4. **Identify policy gaps or violations** if evident in the data
5. **Suggest concrete next steps** for supply chain management
6. **Maintain professional executive summary tone**

### Synthesis Guidelines:
- Start with the key insight that addresses the question
- Support with specific data points
- Reference relevant policies and requirements
- Conclude with recommended actions
- Keep response focused and actionable (3-5 paragraphs max)

### Comprehensive Business Analysis:"""

# Factory functions for easy access
class PromptFactory:
    """Factory class for generating prompts with default configurations"""
    
    @staticmethod
    def create_sql_prompt(question: str, schema_info: str, **kwargs) -> str:
        return PromptTemplates.get_sql_generation_prompt(question, schema_info, **kwargs)
    
    @staticmethod
    def create_validation_prompt(sql: str, question: str, **kwargs) -> str:
        return PromptTemplates.get_sql_validation_prompt(sql, question, **kwargs)
    
    @staticmethod
    def create_rag_prompt(question: str, documents: List[Dict[str, Any]], **kwargs) -> str:
        return PromptTemplates.get_rag_synthesis_prompt(question, documents, **kwargs)
    
    @staticmethod
    def create_intent_prompt(question: str, **kwargs) -> str:
        return PromptTemplates.get_intent_classification_prompt(question, **kwargs)
    
    @staticmethod
    def create_explanation_prompt(query: str, results: Dict[str, Any], query_type: str, **kwargs) -> str:
        return PromptTemplates.get_result_explanation_prompt(query, results, query_type, **kwargs)
    
    @staticmethod
    def create_error_prompt(error: str, query: str, **kwargs) -> str:
        return PromptTemplates.get_error_diagnosis_prompt(error, query, **kwargs)
    
    @staticmethod
    def create_security_prompt(query: str, **kwargs) -> str:
        return PromptTemplates.get_security_analysis_prompt(query, **kwargs)
    
    @staticmethod
    def create_hybrid_prompt(sql_result: Dict[str, Any], policy_result: Dict[str, Any], question: str, **kwargs) -> str:
        return PromptTemplates.get_hybrid_synthesis_prompt(sql_result, policy_result, question, **kwargs)

# Configuration for different validation levels
VALIDATION_CONFIGS = {
    "basic": {
        "enable_security_analysis": False,
        "enable_performance_analysis": False,
        "enable_ai_validation": False,
        "max_retries": 1
    },
    "moderate": {
        "enable_security_analysis": True,
        "enable_performance_analysis": True,
        "enable_ai_validation": True,
        "max_retries": 2
    },
    "strict": {
        "enable_security_analysis": True,
        "enable_performance_analysis": True,
        "enable_ai_validation": True,
        "enable_critique_loop": True,
        "max_retries": 3
    },
    "paranoid": {
        "enable_security_analysis": True,
        "enable_performance_analysis": True,
        "enable_ai_validation": True,
        "enable_critique_loop": True,
        "enable_human_review_simulation": True,
        "max_retries": 5
    }
}