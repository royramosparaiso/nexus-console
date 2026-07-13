# nexus-console

Control plane for Nexus OS. FastAPI + SQLAlchemy async + Postgres.

See the [main repo README](../README.md) for the full story.

## Local dev

```bash
cd console
python -m venv .venv && source .venv/bin/activate
pip install -e /path/to/nexus-core/python
pip install -e ".[dev]"
pytest -q
```

## Docker

The image is built from this directory. `nexus-core` must be vendored at
`vendor/nexus-core/` before running `docker build .` (CI does this automatically).
