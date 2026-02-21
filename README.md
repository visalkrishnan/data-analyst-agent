# 📊 Agentic Data Analyst (LangGraph + DuckDB)

![Python](https://img.shields.io/badge/Python-3.11-blue.svg) ![LangGraph](https://img.shields.io/badge/LangGraph-v1-brightgreen.svg) ![DuckDB](https://img.shields.io/badge/DuckDB-Fast%20OLAP-yellow.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-API-green.svg)

## 📖 Project Overview

This project is an intelligent **Text-to-SQL AI Assistant**. It allows users to upload large structured datasets (CSV or Excel files) and ask natural language questions about them. 

Instead of struggling with context window limits or hallucinated math, this system uses **DuckDB** to execute real SQL queries. A team of AI agents orchestrated by **LangGraph** works together to understand the question, fix typos in the user's prompt, write the SQL code, execute it, fix its own errors, and return a plain English answer.

---

## 🏗️ System Architecture

The workflow uses a multi-agent state machine. Here is how the agents collaborate to solve a user's question:

```mermaid
graph TD
    START((User Query)) --> Router["Agent 1: Router<br/><i>(Is this a data question?)</i>"]
    
    Router -- "General Chat" --> Synthesizer["Agent 4: Synthesizer<br/><i>(Writes the final answer)</i>"]
    Router -- "Database Query" --> Mapper["Agent 2: Mapper<br/><i>(Fixes typos & matches names)</i>"]
    
    Mapper --> SQL["Agent 3: SQL Architect<br/><i>(Writes DuckDB SQL)</i>"]
    SQL --> Executor{"Tool: DB Executor<br/><i>(Runs SQL on DuckDB)</i>"}
    
    Executor -- "SQL Error (Retry up to 3x)" --> SQL
    Executor -- "Success" --> Synthesizer
    
    Synthesizer --> END((Final Response))

    style Executor fill:#f9f,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    style Router fill:#bbf,stroke:#333,stroke-width:2px
    style Mapper fill:#bbf,stroke:#333,stroke-width:2px
    style SQL fill:#bbf,stroke:#333,stroke-width:2px
    style Synthesizer fill:#bfb,stroke:#333,stroke-width:2px


    
If your README.md is looking like one giant block of code or the headers aren't showing up correctly, it is usually because the hidden "markdown" backticks (```) got copied by mistake, or there are missing blank lines.
Here is the perfectly formatted version.
Instructions:
Open your README.md file.
Delete everything currently in it.
Click the "Copy" button at the top right of the code block below.
Paste it into your file and save.
code
Markdown
# 📊 Agentic Data Analyst (LangGraph + DuckDB)

![Python](https://img.shields.io/badge/Python-3.11-blue.svg) ![LangGraph](https://img.shields.io/badge/LangGraph-v1-brightgreen.svg) ![DuckDB](https://img.shields.io/badge/DuckDB-Fast%20OLAP-yellow.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-API-green.svg)

## 📖 Project Overview

This project is an intelligent **Text-to-SQL AI Assistant**. It allows users to upload large structured datasets (CSV or Excel files) and ask natural language questions about them. 

Instead of struggling with context window limits or hallucinated math, this system uses **DuckDB** to execute real SQL queries. A team of AI agents orchestrated by **LangGraph** works together to understand the question, fix typos in the user's prompt, write the SQL code, execute it, fix its own errors, and return a plain English answer.

---

## 🏗️ System Architecture

The workflow uses a multi-agent state machine. Here is how the agents collaborate to solve a user's question:

```mermaid
graph TD
    START((User Query)) --> Router["Agent 1: Router<br/><i>(Is this a data question?)</i>"]
    
    Router -- "General Chat" --> Synthesizer["Agent 4: Synthesizer<br/><i>(Writes the final answer)</i>"]
    Router -- "Database Query" --> Mapper["Agent 2: Mapper<br/><i>(Fixes typos & matches names)</i>"]
    
    Mapper --> SQL["Agent 3: SQL Architect<br/><i>(Writes DuckDB SQL)</i>"]
    SQL --> Executor{"Tool: DB Executor<br/><i>(Runs SQL on DuckDB)</i>"}
    
    Executor -- "SQL Error (Retry up to 3x)" --> SQL
    Executor -- "Success" --> Synthesizer
    
    Synthesizer --> END((Final Response))

    style Executor fill:#f9f,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    style Router fill:#bbf,stroke:#333,stroke-width:2px
    style Mapper fill:#bbf,stroke:#333,stroke-width:2px
    style SQL fill:#bbf,stroke:#333,stroke-width:2px
    style Synthesizer fill:#bfb,stroke:#333,stroke-width:2px
🤖 Meet the Agents (How it Works)
The system relies on 4 specialized agents and 1 execution tool. Here is what they do in simple terms:
1. The Router (The "Traffic Cop")
Purpose: Looks at the user's prompt and decides where to send it.
Logic: If the user says "Hello," it routes directly to the Synthesizer. If the user asks "What was the revenue in 2024?", it routes to the Data pipeline.
2. The Mapper (The "Spell Checker")
Purpose: Solves the "Fuzzy Matching" problem. Users rarely type exact database names (e.g., they type "Apple" instead of "Apple Inc.").
Logic: It uses an AI Vector Database (FAISS) to search the user's text against the actual values in the Excel file. It rewrites the user's question to use the exact, correct spelling before writing any code.
3. The SQL Architect (The "Coder")
Purpose: Writes the actual data query.
Logic: It looks at the database schema (columns and data types) and the cleaned question from the Mapper. It then generates valid, optimized DuckDB SQL code to calculate the answer.
4. The Executor (The "Database Engine")
Purpose: Runs the SQL code on DuckDB.
Superpower (Self-Correction): If the SQL Architect writes bad code (e.g., misspelled a column name), the database throws an error. The Executor catches this error, sends it back to the SQL Architect, and says, "Try again, here is the error."
5. The Synthesizer (The "Spokesperson")
Purpose: Translates raw database rows into a human-friendly sentence.
Logic: It takes the raw JSON/Number from the database (e.g., [{"Total": 5000}]) and replies to the user: "The total revenue was $5,000."
🚀 Setup & Installation
Prerequisites: Docker and Docker Compose installed on your machine.
1. Clone the repository and enter the directory:
code
Bash
git clone https://github.com/YOUR_USERNAME/data-analyst-agent.git
cd data-analyst-agent
2. Create the environment file:
Copy the example file and add your Azure OpenAI keys.
code
Bash
cp .env.example .env
3. Build and start the application:
code
Bash
docker-compose up --build
4. Access the API Documentation:
Open your browser and navigate to: http://localhost:8080/docs
⚡ Usage Example
Step 1: Upload your Data (Ingest)
Upload a .csv or .xlsx file using the /ingest endpoint.
Behind the scenes: The system loads this into lightning-fast DuckDB and maps the unique text entities to FAISS.
Step 2: Ask a Question (Query)
Send a POST request to /query:
code
JSON
{
  "question": "What is the total revenue for Apple in 2024?"
}
Expected Output:
code
JSON
{
  "answer": "The total revenue for Apple Inc. in 2024 was $383 Billion USD.",
  "generated_sql": "SELECT SUM(Revenue) FROM dataset WHERE Company_Name = 'Apple Inc.' AND Year = 2024;"
}
code
Code
### What was likely wrong before?
1. Sometimes Mermaid diagrams break GitHub's renderer if the lines inside the diagram contain weird spacing or missing quotes. I simplified the Mermaid syntax in this version so GitHub renders it flawlessly.
2. Make sure there is an empty line before and after the ```mermaid block.
3. Make sure there is an empty line before and after lists (like step 1, step 2).

Push this to GitHub (`git add README.md`, `git commit -m "fix readme"`, `git push`), and it will look perfect.
