# Contributing

## Atomic commits

Each file or logical change should commit via:

```bash
python tools/auto_commit.py "message" path/to/file
```

## Tests

```bash
make install && make test
```

## Adding an agent

1. Subclass `BaseSubAgent` in `manus_agent/agents/`
2. Register node in `manus_agent/core/graph.py`
3. Document in `docs/AGENTS.md`
4. Add tests under `tests/`
