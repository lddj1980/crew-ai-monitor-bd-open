# crew-ai-monitor-bd

Example project using **CrewAI** with the **OpenAI** API to monitor databases and execute reprocessing routines. The workflow is driven by three autonomous agents that run sequentially.

## Overview

The `main.py` script schedules `run_once()` to run at fixed intervals. At each run the configured SQL is executed, its result is analyzed and then an action is taken. Every step relies on an OpenAI model to interpret results and generate text.

### Agent Diagram
```mermaid
flowchart TD
    Schedule["Scheduler"] -->|RUN_INTERVAL_MINUTES| RunOnce
    subgraph Crew
        Monitor["Monitor Agent"] --> Coordinator["Coordinator Agent"]
        Coordinator --> Executor["Executor Agent"]
    end
    RunOnce --> Monitor
    Executor --> Output["Files in OUTPUT_DIR"]
```

## Quick Setup

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in the variables. At minimum `OPENAI_API_KEY` and `MONITOR_SQL` must be provided.
3. Run the workflow:
   ```bash
   python main.py
   ```

The script runs continuously according to `RUN_INTERVAL_MINUTES`. Outputs from each agent are saved under `OUTPUT_DIR`.

## Key Environment Variables

- `MONITOR_SQL` &ndash; SQL query to be executed.
- `DATABASE_URI` &ndash; database connection string (defaults to local SQLite).
- `OPENAI_API_KEY` &ndash; your OpenAI API key.
- `OPENAI_MODEL` &ndash; model to use (defaults to `gpt-3.5-turbo`).
- `LLM_TEMPERATURE` &ndash; controls randomness of the answers.
- `PROMPTS_FILE` &ndash; path to the JSON file with agent prompts.
- `OUTPUT_DIR` &ndash; folder where log files will be stored.
- `RUN_INTERVAL_MINUTES` &ndash; interval between workflow executions.

Basic example of `.env`:
```env
MONITOR_SQL=SELECT COUNT(*) FROM users;
DATABASE_URI=postgresql+psycopg2://user:pass@localhost/db
OPENAI_API_KEY=sk-...
```

## Customizing Prompts

The `prompts.json` file defines messages and goals for each agent. Placeholders such as `{rows}` and `{decision}` are substituted automatically. Example:
```json
{
  "coordinator_prompt": "Analise os resultados: {rows} e decida se precisa reprocessar.",
  "executor_prompt": "Recebida a decisao '{decision}', execute o reprocessamento se necessario."
}
```

### Summary Flow
```mermaid
sequenceDiagram
    participant Scheduler
    participant Monitor
    participant Coordinator
    participant Executor
    Scheduler->>Monitor: Run MONITOR_SQL
    Monitor->>Coordinator: Result as text
    Coordinator->>Executor: Decision and instructions
    Executor-->>Scheduler: Final report
```

This provides a starting point for creating automated monitoring and response routines using only OpenAI infrastructure.
