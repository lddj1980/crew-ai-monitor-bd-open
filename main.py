from crewai_config.monitor_agent import build_monitor_agent, execute_monitor_sql
from crewai_config.coordinator_agent import build_coordinator_agent
from crewai_config.executor_agent import build_executor_agent
from crewai_config.utils import load_env, load_prompts, save_output, parse_sql_result
import os
import schedule
import time


load_env()

# Interval in minutes between each run of ``run_once``
RUN_INTERVAL_MINUTES = int(os.getenv("RUN_INTERVAL_MINUTES", "1"))

PROMPTS_FILE = os.getenv("PROMPTS_FILE", "prompts.json")


def run_once():
    prompts = load_prompts(PROMPTS_FILE)

    # Monitor step
    raw_result = execute_monitor_sql()
    save_output("monitor", raw_result)
    rows = parse_sql_result(raw_result)
    first = rows[0] if rows else {}

    # Coordinator step
    coordinator = build_coordinator_agent(PROMPTS_FILE)
    coord_prompt = prompts.get("coordinator_prompt", "{rows}").format(rows=rows, **first)
    coord_output = coordinator.kickoff(coord_prompt)
    save_output("coordinator", str(coord_output))

    # Executor step
    executor = build_executor_agent(PROMPTS_FILE)
    exec_prompt = prompts.get("executor_prompt", "{decision}").format(decision=str(coord_output), **first)
    exec_output = executor.kickoff(exec_prompt)
    save_output("executor", str(exec_output))

    print(exec_output)
if __name__ == "__main__":
    schedule.every(RUN_INTERVAL_MINUTES).minutes.do(run_once)
    while True:
        schedule.run_pending()
        time.sleep(1)
