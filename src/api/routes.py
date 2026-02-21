import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.api.schemas import QueryRequest, QueryResponse
from src.utils.db_setup import ingest_file_to_db
from src.graph.workflow import create_data_graph

router = APIRouter()
data_graph = create_data_graph()

@router.post("/ingest")
async def ingest_data(file: UploadFile = File(...)):
    """Uploads CSV/Excel, loads into DuckDB, and builds Vector dictionary."""
    try:
        os.makedirs("temp", exist_ok=True)
        file_path = f"temp/{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
            
        columns = ingest_file_to_db(file_path)
        os.remove(file_path) # cleanup
        
        return {"status": "success", "message": "Data ingested and indexed successfully.", "columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_data(request: QueryRequest):
    """Executes the Agentic SQL Workflow."""
    try:
        result = data_graph.invoke({"question": request.question})
        return QueryResponse(
            answer=result.get("final_answer", "Error generating answer."),
            generated_sql=result.get("generated_sql", "N/A")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))