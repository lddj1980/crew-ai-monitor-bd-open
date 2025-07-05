import os
from crewai import Agent, Crew, Task
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from .utils import get_llm, load_prompts, get_database


def execute_monitor_sql():
    """Execute the SQL statement provided in ``MONITOR_SQL`` env variable.

    Returns:
        str: result returned by ``SQLDatabase.run``
    """
    query = os.getenv("MONITOR_SQL")
    if not query:
        raise ValueError("MONITOR_SQL environment variable is not set")

    # Use the configured database
    db = get_database()
    return db.run(query, include_columns=True)


def build_monitor_agent(prompts_path: str = "prompts.json") -> Agent:
    prompts = load_prompts(prompts_path)
    sql_tool = QuerySQLDataBaseTool(db=get_database())

    agent = Agent(
        role=prompts.get("monitor_role", "Database Monitor"),
        goal=prompts.get(
            "monitor_goal", "Executar MONITOR_SQL e retornar o resultado"
        ),
        backstory=prompts.get("monitor_backstory", ""),
        tools=[sql_tool],
        llm=get_llm(),
        allow_delegation=False,
    )
    return agent


def run_monitor_crew(prompts_path: str = "prompts.json"):
    """Run MONITOR_SQL through a simple CrewAI agent and return the result."""
    query = os.getenv("MONITOR_SQL")
    if not query:
        raise ValueError("MONITOR_SQL environment variable is not set")

    agent = build_monitor_agent(prompts_path)

    task = Task(
        description="Execute the query: {query}",
        expected_output="Result from the SQL query",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task])
    return crew.kickoff(inputs={"query": query})
