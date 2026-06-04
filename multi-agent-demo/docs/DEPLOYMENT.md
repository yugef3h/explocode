# Deployment

## Requirements

- Python 3.11+
- Optional: `OPENAI_API_KEY` when `MANUS_LLM_PROVIDER=openai`

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `MANUS_LLM_PROVIDER` | `mock` | `mock` or `openai` |
| `MANUS_OPENAI_MODEL` | `gpt-4o-mini` | Model name |
| `MANUS_DATA_DIR` | `.manus_data` | SQLite + artifacts |

## Docker (sketch)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY multi-agent-demo .
RUN pip install -e .
CMD ["manus", "run", "Daily report"]
```

## Observability

- Inspect SQLite `memories` per `run_id`
- Ship `report.md` artifacts to S3 or internal wiki
