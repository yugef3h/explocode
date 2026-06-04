# Manus-Style Multi-Agent Demo

Production-oriented Python multi-agent orchestration inspired by [Manus](https://manus.im): a **supervisor** decomposes work, **sub-agents** plan / research / execute / write, and **memory** persists context across steps.

## Quickstart

```bash
cd multi-agent-demo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Mock mode (no API key)
manus run "Write a brief report on LangGraph orchestration patterns"

# With OpenAI
export OPENAI_API_KEY=sk-...
manus run "Analyze multi-agent memory strategies" --llm openai
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

| Doc | Description |
|-----|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design |
| [AGENTS.md](docs/AGENTS.md) | Sub-agent roles |
| [MEMORY.md](docs/MEMORY.md) | Storage model |
| [API.md](docs/API.md) | Python API |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Ops notes |

## Development

Atomic commits during development:

```bash
python scripts/auto_commit.py "message" path/to/file.py
```

## License

MIT
