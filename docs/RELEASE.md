# Release checklist

Use this before creating a public Runtrace release.

## 1. Update version

Update the version in:

- `pyproject.toml`
- `src/runtrace/__init__.py`

Keep them in sync.

## 2. Run tests and lint

```bash
python -m pip install -e '.[dev]'
ruff check .
pytest -q
```

## 3. Run local smoke test

```bash
runtrace --help
python -m runtrace --help
runtrace demo
runtrace list
runtrace show latest
runtrace report
```

## 4. Run non-editable install smoke test

From outside the repository:

```bash
python -m venv /tmp/runtrace-test-venv
source /tmp/runtrace-test-venv/bin/activate
pip install /path/to/runtrace
runtrace --help
runtrace demo
runtrace list
runtrace show latest
runtrace report
python -m runtrace --help
```

## 5. Update changelog

Move items from `Unreleased` into a versioned section, for example:

```markdown
## 0.1.0 - YYYY-MM-DD
```

## 6. Create tag

```bash
git tag v0.1.0
git push origin v0.1.0
```

## 7. Create GitHub release

Use the changelog notes. Include the current limitations honestly.

## 8. PyPI later

Do not configure PyPI publishing until:

- package name availability is checked
- project URLs are final
- trusted publishing or credentials are configured
- at least one non-editable install test passes from a clean environment
