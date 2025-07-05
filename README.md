# crew-ai-monitor-bd

Example project using **CrewAI** with the **OpenAI** API to monitor databases and trigger automated actions. Three autonomous agents work together to interpret query results and decide what to do next.

## Overview

The `main.py` script schedules `run_once()` to run at fixed intervals. In each cycle a SQL query is executed, the result is analyzed and a follow-up action is triggered. Every step relies on an OpenAI model to interpret results and generate text.

### Agent Diagram
```mermaid
flowchart TD
    Schedule["Scheduler"] -->|RUN_INTERVAL_MINUTES| RunOnce
    subgraph Crew
        Monitor["Monitor Agent"] --> Coordinator["Coordinator Agent"]
        Coordinator --> Action["Action Agent"]
    end
    RunOnce --> Monitor
    Action --> Output["Actions (files or integrations)"]
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

The `prompts.json` file defines messages and goals for each agent. Placeholders such as `{rows}` and `{decision}` are substituted automatically. A minimal example could be:
```json
{
  "coordinator_prompt": "Analise os resultados: {rows} e descreva a ação necessária.",
  "executor_prompt": "Recebida a decisão '{decision}', realize a ação indicada."
}
```

### Summary Flow
```mermaid
sequenceDiagram
    participant Scheduler
    participant Monitor
    participant Coordinator
    participant ActionAgent
    Scheduler->>Monitor: Run MONITOR_SQL
    Monitor->>Coordinator: Result as text
    Coordinator->>ActionAgent: Decision and instructions
    ActionAgent-->>Scheduler: Final report
```

This provides a starting point for creating automated monitoring and response routines using only OpenAI infrastructure.

## Potential Extensions

The current implementation writes the results from each agent to text files. In a real-world deployment the same decisions could be used to:

- invoke external APIs or microservices
- send email or WhatsApp notifications
- trigger business workflows when certain conditions are met
- gather customer feedback after a specific event, such as asking a traveller to review an itinerary when they return from a trip

By adapting the executor agent you can integrate virtually any action into the workflow.
