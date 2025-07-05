# crew-ai-monitor-bd


To run this project you will need to provide your LLM API credentials locally.
1. Copy `.env.example` to `.env`.
2. Keep the `.env` file out of version control.
3. Set `MONITOR_SQL` with the SQL statement you want the monitoring agent to execute. Optionally, set `DATABASE_URI` to define the database connection string.
4. Provide your OpenAI key in `OPENAI_API_KEY`.
5. `PROMPTS_FILE` sets the JSON file containing the agents' prompts (defaults to `prompts.json`).
6. `OUTPUT_DIR` defines where each agent writes its output files (defaults to `outputs`).
7. `LLM_TEMPERATURE` controls the randomness of the model (defaults to `0`).
8. `OPENAI_MODEL` chooses the OpenAI model (defaults to `gpt-3.5-turbo`).
9. `RUN_INTERVAL_MINUTES` sets how often the workflow runs (defaults to `1`).

The `get_llm` helper reads these variables to construct the language model.
It requires `OPENAI_API_KEY` and returns a `ChatOpenAI` instance configured with
`OPENAI_MODEL` and `LLM_TEMPERATURE`.

```
MONITOR_SQL=SELECT COUNT(*) FROM users;
DATABASE_URI=postgresql+psycopg2://user:pass@localhost/db
```

### Schemas

`DATABASE_URI` picks the database but does **not** set the schema. If your tables
reside outside the default `public` schema, reference them explicitly or adjust
the connection `search_path`:

```
MONITOR_SQL=SELECT * FROM public.produto
DATABASE_URI=postgresql+psycopg2://user:pass@localhost/dbname?options=-csearch_path%3Dmyschema
```

### Temporary database for tests

For an ephemeral setup you can point `DATABASE_URI` to an in-memory SQLite
database:

```
DATABASE_URI=sqlite:///:memory:
```

After copying `.env.example` to `.env` and adjusting the values you can run the
workflow with:

```bash
python main.py
```

The query can be executed using `execute_monitor_sql`:

```python
from crewai_config.monitor_agent import execute_monitor_sql

result = execute_monitor_sql()
print(result)
```

Placeholders are replaced using values from the first row of the result.

Example `prompts.json`
----------------------

The prompts file can define custom messages for the agents. The text may
contain placeholders that are replaced when the workflow runs.

```json
{
  "coordinator_prompt": "Analise os resultados: {rows} e decida se precisa reprocessar.",
  "executor_prompt": "Recebida a decisao '{decision}', execute o reprocessamento se necessario."
}
```

Available placeholders:

* `{rows}` &ndash; list of dictionaries returned by `parse_sql_result`.
* Column names from the first row of the result, for example `{count}`.
* `{decision}` &ndash; the decision text produced by the coordinator agent.

All placeholders are filled with values obtained from `parse_sql_result` in
`main.py` before being sent to the agents.
