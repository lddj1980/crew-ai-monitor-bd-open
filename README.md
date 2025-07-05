# crew-ai-monitor-bd

Projeto de exemplo que utiliza **CrewAI** com a API da **OpenAI** para monitorar bancos de dados e executar rotinas de reprocessamento. O fluxo de trabalho é conduzido por três agentes autônomos que atuam em sequência.

## Visão Geral

O script `main.py` agenda a função `run_once()` em intervalos definidos. A cada execução, o SQL configurado é executado, seu resultado é analisado e uma ação é tomada. Todos os passos utilizam um modelo da OpenAI para interpretar e gerar texto.

### Diagrama dos Agentes
```mermaid
flowchart TD
    Schedule["Agendador"] -->|RUN_INTERVAL_MINUTES| RunOnce
    subgraph Crew
        Monitor["Monitor Agent"] --> Coordinator["Coordinator Agent"]
        Coordinator --> Executor["Executor Agent"]
    end
    RunOnce --> Monitor
    Executor --> Output["Arquivos em OUTPUT_DIR"]
```

## Configuração Rápida

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Copie `.env.example` para `.env` e ajuste as variáveis. Pelo menos `OPENAI_API_KEY` e `MONITOR_SQL` devem ser definidos.
3. Rode o workflow:
   ```bash
   python main.py
   ```

O script executa continuamente de acordo com `RUN_INTERVAL_MINUTES`. Os resultados de cada agente são gravados em arquivos dentro de `OUTPUT_DIR`.

## Variáveis de Ambiente Principais

- `MONITOR_SQL` &ndash; consulta SQL que será executada.
- `DATABASE_URI` &ndash; string de conexão do banco (padrão SQLite local).
- `OPENAI_API_KEY` &ndash; chave de acesso à API da OpenAI.
- `OPENAI_MODEL` &ndash; modelo a ser utilizado (padrao `gpt-3.5-turbo`).
- `LLM_TEMPERATURE` &ndash; controla a aleatoriedade das respostas.
- `PROMPTS_FILE` &ndash; caminho do JSON com prompts dos agentes.
- `OUTPUT_DIR` &ndash; pasta onde os arquivos de log serão salvos.
- `RUN_INTERVAL_MINUTES` &ndash; intervalo entre execuções da rotina.

Exemplo básico de `.env`:
```env
MONITOR_SQL=SELECT COUNT(*) FROM users;
DATABASE_URI=postgresql+psycopg2://user:pass@localhost/db
OPENAI_API_KEY=sk-...
```

## Personalizando os Prompts

O arquivo `prompts.json` define mensagens e objetivos de cada agente. Placeholder como `{rows}` e `{decision}` são substituídos automaticamente. Um exemplo:
```json
{
  "coordinator_prompt": "Analise os resultados: {rows} e decida se precisa reprocessar.",
  "executor_prompt": "Recebida a decisao '{decision}', execute o reprocessamento se necessario."
}
```

### Fluxo Resumido
```mermaid
sequenceDiagram
    participant Scheduler
    participant Monitor
    participant Coordinator
    participant Executor
    Scheduler->>Monitor: Executa MONITOR_SQL
    Monitor->>Coordinator: Resultado em texto
    Coordinator->>Executor: Decisao e instruções
    Executor-->>Scheduler: Relatório final
```

Com isso você tem um ponto de partida para criar rotinas automatizadas de monitoramento e resposta utilizando apenas a infraestrutura da OpenAI.
