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
    %% Nodes
    START((User Query))
    Router{"Agent 1: Router<br/>(Is this a data question?)"}
    Mapper["Agent 2: Mapper<br/>(Fixes typos & matches names)"]
    SQL["Agent 3: SQL Architect<br/>(Writes DuckDB SQL)"]
    Executor[["Tool: DB Executor<br/>(Runs SQL on DuckDB)"]]
    Synthesizer["Agent 4: Synthesizer<br/>(Writes the final answer)"]
    END((Final Response))

    %% Flow
    START --> Router
    
    Router -- "General Chat" --> Synthesizer
    Router -- "Database Query" --> Mapper
    
    Mapper --> SQL
    SQL --> Executor
    
    %% Self-Correction Loop
    Executor -- "SQL Error (Retry up to 3x)" --> SQL
    Executor -- "Success" --> Synthesizer
    
    Synthesizer --> END
