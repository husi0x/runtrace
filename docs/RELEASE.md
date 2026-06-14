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
bash scripts/smoke.sh
runtrace --help
python -m runtrace --help
runtrace init --force
runtrace demo
runtrace index
runtrace export --output summary.json
python -m json.tool summary.json >/dev/null
runtrace list
runtrace show latest
runtrace report
runtrace open --help
```

## 4. Run PyPI-style install smoke test

Test the public install path in a clean environment:

```bash
python -m venv /tmp/runtrace-test-venv
source /tmp/runtrace-test-venv/bin/activate
pip install runtrace
runtrace --help
runtrace demo
runtrace index
runtrace export --output summary.json
python -m json.tool summary.json >/dev/null
runtrace list
runtrace show latest
runtrace report
runtrace open --help
python -m runtrace --help
```

## 5. Build and check distributions

See [PYPI.md](PYPI.md) for PyPI package maintenance.

```bash
python -m pip install build twine
rm -rf dist build *.egg-info
python -m build
twine check dist/*
```

## 6. Test install the wheel locally

```bash
python -m venv /tmp/runtrace-wheel-test
source /tmp/runtrace-wheel-test/bin/activate
pip install dist/*.whl
runtrace demo
runtrace open --help
```

## 7. Update changelog

Move items from `Unreleased` into a versioned section, for example:

```markdown
## X.Y.Z - YYYY-MM-DD
```

## 8. Create tag

Only after all checks pass:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

Do not force-push tags.

## 9. Create GitHub release

Use the changelog notes. Include the current limitations honestly.

## 10. Publish future versions to PyPI manually

Runtrace is already published at <https://pypi.org/project/runtrace/>. For future versions, follow [PYPI.md](PYPI.md):

```bash
twine upload dist/*
```

Do not commit credentials, tokens, `.pypirc`, or environment files. Prefer project-scoped PyPI tokens for `runtrace`.
