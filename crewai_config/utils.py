import os
import json
from dotenv import load_dotenv


def load_env(path: str = ".env"):
    """Load environment variables from a file."""
    if os.path.exists(path):
        load_dotenv(path)

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
    """Return the OpenAI LLM configured via environment variables."""

    temperature = float(os.environ.get("LLM_TEMPERATURE", "0"))
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set")

    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    return ChatOpenAI(api_key=api_key, model=model, temperature=temperature)


def load_prompts(path: str = "prompts.json"):
    """Load agent prompts from a JSON file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompts file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
