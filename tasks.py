"""pyinvoke tasks for eco-spec-tracker. Mirrors the pattern in eco-mcp-app."""

from __future__ import annotations

from invoke import task


@task
def sync(c):  # type: ignore[no-untyped-def]
    """Install deps via uv."""
    c.run("uv sync --group dev")


@task
def test(c):  # type: ignore[no-untyped-def]
    """Run the pytest smoke suite."""
    c.run("uv run pytest")


@task
def ruff(c):  # type: ignore[no-untyped-def]
    """Lint + format (check mode)."""
    c.run("uv run ruff check src tests tasks.py")
    c.run("uv run ruff format --check src tests tasks.py")


@task
def fmt(c):  # type: ignore[no-untyped-def]
    """Apply ruff formatting."""
    c.run("uv run ruff check --fix src tests tasks.py")
    c.run("uv run ruff format src tests tasks.py")


@task
def precommit(c):  # type: ignore[no-untyped-def]
    """Run all pre-commit hooks against every file."""
    c.run("uv run pre-commit run --all-files")


@task(help={"port": "Port for the FastAPI dev server (default: 4100)."})
def run(c, port=4100):  # type: ignore[no-untyped-def]
    """Run the FastAPI server with autoreload + browser livereload."""
    c.run(
        "DEBUG=1 uv run uvicorn eco_spec_tracker.main:app "
        f"--reload --reload-dir src --port {port} --host 0.0.0.0"
    )
