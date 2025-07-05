from crewai import Agent
from .utils import get_llm, load_prompts


def build_coordinator_agent(prompts_path: str = "prompts.json"):
    prompts = load_prompts(prompts_path)
    llm = get_llm()

    agent = Agent(
        role=prompts.get("coordinator_role", "Coordenador"),
        goal=prompts.get(
            "coordinator_goal",
            "Analisar resultados do monitor e decidir se deve reprocessar",
        ),
        backstory=prompts.get("coordinator_backstory", ""),
        llm=llm,
        verbose=True,
    )
    return agent
