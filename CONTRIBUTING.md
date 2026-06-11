# Contributing to Runtrace

Thanks for helping improve Runtrace. Keep changes small, practical, and easy to review.

## Setup

```bash
git clone https://github.com/husi0x/runtrace.git
cd runtrace

python -m venv .venv
source .venv/bin/activate

pip install -e '.[dev]'
```

## Run the full smoke check

```bash
bash scripts/smoke.sh
```

## Run tests

```bash
pytest
```

## Lint

```bash
ruff check .
```

## Smoke test the CLI

```bash
runtrace --help
runtrace demo
runtrace list
runtrace show latest
runtrace report
```

## Making a small PR

1. Pick one focused change.
2. Add or update tests if behavior changes.
3. Run `pytest` and `ruff check .`.
4. Update docs if user-facing behavior changes.
5. Open the PR with a short explanation and before/after notes.

Good PRs are usually small:

- better error message
- new checklist heuristic
- report formatting improvement
- CLI docs fix
- test coverage for an edge case

Avoid mixing unrelated changes in one PR.
