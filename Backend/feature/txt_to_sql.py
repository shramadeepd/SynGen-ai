import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from pathlib import Path

from agno.agent import Agent, RunResponse
from agno.models.ollama import Ollama

import sys
sys.path.append('..')
from templates.sql_templates import SQL_GENERATION_SYSTEM_PROMPT

from agno.agent import Agent, RunResponse
from agno.models.google import Gemini

from google import genai
from google.genai import types

def validate_query_safety(query: str) -> bool:
    # Check for dangerous patterns
    dangerous_patterns = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER']
    return not any(pattern.lower() in query.lower() for pattern in dangerous_patterns)

def validate_query_format(query: str) -> bool:
    # Basic SQL validation
    required_patterns = ['SELECT', 'FROM']
    return all(pattern.lower() in query.lower() for pattern in required_patterns)

question = "What is the total sales amount for all orders?"

# Initialize the SQL generation agent
agent = Agent(
    model=Gemini(id="gemini-2.0-flash"),
    markdown=True,
    description=SQL_GENERATION_SYSTEM_PROMPT.format(question=question)
)

# Get the response
response = agent.run(question)

# Extract SQL query from the response (assuming it's in a code block)
sql_query = response.content  # You might need to parse this based on actual response format


def format_sql_query(query: str) -> str:
    # Format the SQL query for better readability
    return query.strip('`').strip('sql').strip()

# Validate the query
if validate_query_safety(sql_query) and validate_query_format(sql_query):
    print(format_sql_query(sql_query))
else:
    print("Query validation failed. Please try again.")


