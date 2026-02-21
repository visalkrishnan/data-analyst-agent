from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
import json

from src.utils.config import get_llm
from src.utils.db_setup import get_db_schema, execute_sql, get_similar_entities
from src.graph.state import AgentState

def print_state(node, state):
    print(f"\n--- NODE: {node} ---")

# --- 1. Router ---
class RouterOutput(BaseModel):
    intent: str = Field(description="'database' if query requires data analysis, else 'general'")

def router_node(state: AgentState):
    print_state("Router", state)
    llm = get_llm().with_structured_output(RouterOutput)
    prompt = ChatPromptTemplate.from_template("Is this query asking about dataset analysis or is it general chat? Query: {question}")
    
    chain = prompt | llm 
    result = chain.invoke({"question": state["question"]})
    
    return {"intent": result.intent, "error_count": 0}

# --- 2. Mapper (Entity Resolution) ---
def mapper_node(state: AgentState):
    """Finds exact database strings for fuzzy terms in the question."""
    print_state("Mapper", state)
    question = state["question"]
    
    similar_entities = get_similar_entities(question)
    
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template("""
    Rewrite the user's question to use the exact database values provided below, if applicable.
    If no exact values apply, return the original question.
    
    Original Question: {question}
    Exact Database Values Available:
    {entities}
    
    Rewritten Question:
    """)
    chain = prompt | llm | StrOutputParser()
    mapped_q = chain.invoke({"question": question, "entities": similar_entities})
    
    return {"mapped_question": mapped_q, "potential_entities": similar_entities}

# --- 3. SQL Architect ---
class SQLOutput(BaseModel):
    sql_query: str = Field(description="The DuckDB SQL query.")

def sql_architect_node(state: AgentState):
    """Generates the SQL query based on the schema and mapped question."""
    print_state("SQL Architect", state)
    schema = get_db_schema()
    llm = get_llm().with_structured_output(SQLOutput)
    
    error_context = ""
    if state.get("sql_error"):
        error_context = f"PREVIOUS ERROR: {state['sql_error']}\nPREVIOUS SQL: {state['generated_sql']}\nFix the SQL!"

    prompt = ChatPromptTemplate.from_template("""
    You are a DuckDB SQL Expert. Write a SQL query to answer the user's question.
    
    SCHEMA:
    {schema}
    
    {error_context}
    
    QUESTION: {question}
    
    RULES:
    1. Output ONLY valid DuckDB SQL.
    2. Ensure column names match the schema exactly.
    3. Use LIMIT 50 to avoid massive outputs unless aggregating.
    """)
    
    # FIX: Chained prompt and llm together
    chain = prompt | llm
    result = chain.invoke({
        "schema": schema, 
        "question": state["mapped_question"],
        "error_context": error_context
    })
    
    print(f"Generated SQL: {result.sql_query}")
    return {"generated_sql": result.sql_query}

# --- 4. Executor ---
def executor_node(state: AgentState):
    """Executes SQL. Handles errors for the self-correction loop."""
    print_state("Executor", state)
    sql = state["generated_sql"]
    
    result, error = execute_sql(sql)
    
    if error:
        print(f"SQL Error: {error}")
        return {"sql_error": error, "sql_result": None, "error_count": state.get("error_count", 0) + 1}
    else:
        print(f"SQL Success. Rows returned: {len(result)}")
        return {"sql_result": result, "sql_error": None}

# --- 5. Synthesizer ---
def synthesizer_node(state: AgentState):
    """Converts raw JSON data into a natural language response."""
    print_state("Synthesizer", state)
    llm = get_llm()
    
    if state["intent"] != "database":
        response = llm.invoke(f"Answer generally: {state['question']}")
        return {"final_answer": response.content}

    prompt = ChatPromptTemplate.from_template("""
    Answer the user's question based strictly on the SQL Data Result.
    
    Question: {question}
    SQL Data Result: {data}
    
    If the data result is empty, say no data was found.
    Format the answer professionally.
    """)
    
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": state["mapped_question"], "data": str(state["sql_result"])})
    
    return {"final_answer": result}