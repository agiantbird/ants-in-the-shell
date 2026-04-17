# Ants in the Shell

A terminal-based ant colony simulation. Ants dig tunnels, forage for food, reproduce, and die.

> ⚠️ Early in development.

## Requirements

- Python 3.12 or newer
- A terminal (macOS Terminal, iTerm2, any Linux terminal, Windows Terminal)

## Setup

Clone the repo, then from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate    # on Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Running

```bash
python -m antfarm
```

Or:

```bash
antfarm
```

## Development

Run the tests:

```bash
pytest
```

Lint and format:

```bash
ruff check .
ruff format .
```
