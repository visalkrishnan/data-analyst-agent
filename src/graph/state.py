from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    question: str
    intent: str # 'database' or 'general'
    
    # Mapper output
    mapped_question: str 
    potential_entities: str
    
    # SQL Architect output
    generated_sql: str
    
    # Executor output
    sql_result: Optional[List[Dict[str, Any]]]
    sql_error: Optional[str]
    error_count: int
    
    # Final Output
    final_answer: str