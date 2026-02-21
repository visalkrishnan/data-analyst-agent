from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(title="Agentic Data Analyst (DuckDB + LangGraph)")

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "Database Agent is running"}