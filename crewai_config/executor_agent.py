from crewai import Agent
from .utils import get_llm, load_prompts


def build_executor_agent(prompts_path: str = "prompts.json"):
    prompts = load_prompts(prompts_path)
    llm = get_llm()

    agent = Agent(
        role=prompts.get("executor_role", "Executor"),
        goal=prompts.get(
            "executor_goal",
            "Realizar o reprocessamento quando solicitado",
        ),
        backstory=prompts.get("executor_backstory", ""),
        llm=llm,
        verbose=True,
    )
    return agent
