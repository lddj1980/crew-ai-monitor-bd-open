import os
import json
from dotenv import load_dotenv


def load_env(path: str = ".env"):
    """Carrega variáveis de ambiente de um arquivo."""
    if os.path.exists(path):
        load_dotenv(path)

from .my_enterprise_llm import MyEnterpriseLLM
from langchain_openai import ChatOpenAI

from langchain_community.utilities.sql_database import SQLDatabase


def get_database():
    """Return a ``SQLDatabase`` using ``DATABASE_URI`` from the environment."""
    uri = os.environ.get("DATABASE_URI", "sqlite:///monitor.db")
    return SQLDatabase.from_uri(uri)


def save_output(name: str, content: str, output_dir: str | None = None) -> str:
    """Save agent output under OUTPUT_DIR and return the file path."""
    directory = output_dir or os.getenv("OUTPUT_DIR", "outputs")
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def parse_sql_result(raw: str):
    """Convert the string result from SQLDatabase.run into Python objects."""
    import ast
    try:
        return ast.literal_eval(raw)
    except Exception:
        return []


def get_llm():
    """Retorna o LLM apropriado.

    Se ``OPENAI_API_KEY`` estiver definido usa ``ChatOpenAI``; caso contrário,
    utiliza ``MyEnterpriseLLM``.
    """
    temperature = float(os.environ.get("LLM_TEMPERATURE", "0"))
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        return ChatOpenAI(api_key=openai_key, model=model, temperature=temperature)

    return MyEnterpriseLLM(
        model=os.environ.get("LLM_MODEL", "mistral-nemo-instruct"),
        client_id=os.environ.get("LLM_CLIENT_ID", ""),
        client_secret=os.environ.get("LLM_CLIENT_SECRET", ""),
        temperature=temperature,
    )


def load_prompts(path: str = "prompts.json"):
    """Carrega os prompts dos agentes de um arquivo JSON."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompts file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
