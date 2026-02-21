import duckdb
import pandas as pd
import os
from langchain_community.vectorstores import FAISS
from src.utils.config import get_embeddings

DB_PATH = "data/dataset.db"
FAISS_PATH = "data/faiss_index"

def ingest_file_to_db(file_path: str):
    """Converts uploaded CSV/Excel to a persistent DuckDB table and indexes entities."""
    os.makedirs("data", exist_ok=True)
    
    # 1. Read file using Pandas
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
        
    # Clean column names (replace spaces with underscores for SQL safety)
    df.columns = [c.strip().replace(' ', '_') for c in df.columns]

    # 2. Save to DuckDB
    con = duckdb.connect(DB_PATH)
    con.execute("DROP TABLE IF EXISTS dataset")
    con.execute("CREATE TABLE dataset AS SELECT * FROM df")
    
    # 3. Build Entity Mapper (FAISS)
    # We index unique values from string columns (e.g., Company Names)
    texts_to_index = []
    for col in df.select_dtypes(include=['object', 'string']).columns:
        unique_vals = df[col].dropna().unique()
        for val in unique_vals:
            texts_to_index.append(f"{col}: {val}")
            
    if texts_to_index:
        embeddings = get_embeddings()
        vectorstore = FAISS.from_texts(texts_to_index, embeddings)
        vectorstore.save_local(FAISS_PATH)
        
    con.close()
    return list(df.columns)

def get_db_schema() -> str:
    """Returns the SQL schema of the dataset."""
    if not os.path.exists(DB_PATH):
        return "No data loaded yet."
    con = duckdb.connect(DB_PATH)
    schema_df = con.execute("PRAGMA table_info('dataset')").df()
    con.close()
    schema_str = "Table 'dataset' columns:\n"
    for _, row in schema_df.iterrows():
        schema_str += f"- {row['name']} ({row['type']})\n"
    return schema_str

def execute_sql(query: str):
    """Executes SQL against DuckDB."""
    con = duckdb.connect(DB_PATH)
    try:
        result = con.execute(query).df()
        return result.to_dict(orient="records"), None
    except Exception as e:
        return None, str(e)
    finally:
        con.close()

def get_similar_entities(query: str, k: int = 3) -> str:
    """Finds exact dataset values matching the user's fuzzy terms."""
    if not os.path.exists(FAISS_PATH):
        return ""
    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    results = vectorstore.similarity_search(query, k=k)
    return "\n".join([doc.page_content for doc in results])