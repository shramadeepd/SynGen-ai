# Features

We are using [Agno](https://docs.agno.com/) for the agentic ai framework

Things can be included

1. Inference engine : It is basically the brain of any ai based system
2. Look for the vectorised database
3. 

## Tex to SQL

In text to sql we will be using api key for the sql qurey generation then we will check if the query is correct through various checks some of them are:

1. LLM based checking
2. Regex based checking
3. READ  only find dangerous patterns no write or delete
4. Check if the query is valid or not

The llm should be able to either give the correct query or None (qurey = generate_sql(ans, none) , error = generate_sql(error, none) )

## RAG for the conversation



LLM model for tts: [SQL Coder doc.](https://ollama.com/library/sqlcoder)

Apply Circuit breaker

Add voice and image input methods