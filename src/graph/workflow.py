from langgraph.graph import StateGraph, START, END
from src.graph.state import AgentState
from src.graph.nodes import (
    router_node, mapper_node, sql_architect_node, 
    executor_node, synthesizer_node
)

def create_data_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("mapper", mapper_node)
    workflow.add_node("sql_architect", sql_architect_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("synthesizer", synthesizer_node)
    
    # 1. Entry
    workflow.add_edge(START, "router")
    
    # 2. Router Logic
    def route_intent(state: AgentState):
        if state["intent"] == "database":
            return "mapper"
        return "synthesizer"
        
    workflow.add_conditional_edges("router", route_intent, {"mapper": "mapper", "synthesizer": "synthesizer"})
    
    # 3. Main Flow
    workflow.add_edge("mapper", "sql_architect")
    workflow.add_edge("sql_architect", "executor")
    
    # 4. Self-Correction Loop Logic
    def route_execution(state: AgentState):
        # If error exists and we haven't tried 3 times, go back to SQL Architect to fix it
        if state["sql_error"] and state["error_count"] < 3:
            return "sql_architect"
        # If success or max retries reached, go to synthesizer
        return "synthesizer"
        
    workflow.add_conditional_edges("executor", route_execution, {"sql_architect": "sql_architect", "synthesizer": "synthesizer"})
    
    # 5. Exit
    workflow.add_edge("synthesizer", END)
    
    return workflow.compile()