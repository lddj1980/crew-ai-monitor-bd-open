# crew-ai-monitor-bd


To run this project you will need to provide your LLM API credentials locally.
1. Copy `.env.example` to `.env`.
2. Fill in `LLM_CLIENT_ID` and `LLM_CLIENT_SECRET` with your real values inside `.env`.
3. Keep the `.env` file out of version control.
4. Set `MONITOR_SQL` with the SQL statement you want the monitoring agent to execute. Optionally, set `DATABASE_URI` to define the database connection string.
5. Optionally, set `SERPRO_CA_BUNDLE` with the path to a trusted certificate bundle if your environment requires a custom CA. SSL verification is enabled by default.
6. If `OPENAI_API_KEY` is defined the agents will use OpenAI; otherwise the proprietary LLM is used.
7. `PROMPTS_FILE` sets the JSON file containing the agents' prompts (defaults to `prompts.json`).
8. `OUTPUT_DIR` defines where each agent writes its output files (defaults to `outputs`).
9. `LLM_MODEL` selects the proprietary LLM model when `OPENAI_API_KEY` is not set (defaults to `mistral-nemo-instruct`).
10. `LLM_TEMPERATURE` controls the randomness of the model for both backends (defaults to `0`).
11. `OPENAI_MODEL` chooses the OpenAI model when `OPENAI_API_KEY` is provided (defaults to `gpt-3.5-turbo`).
12. `RUN_INTERVAL_MINUTES` sets how often the workflow runs (defaults to `1`).

The `get_llm` helper reads these variables to construct the language model. If
`OPENAI_API_KEY` is set, it returns a `ChatOpenAI` instance configured with
`OPENAI_MODEL` and `LLM_TEMPERATURE`. Otherwise it creates `MyEnterpriseLLM`
using `LLM_MODEL`, `LLM_CLIENT_ID`, `LLM_CLIENT_SECRET`, and the same
temperature value.

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
