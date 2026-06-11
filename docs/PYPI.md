# PyPI release prep

Runtrace is prepared so it can be published to PyPI later. Publishing is manual; do not commit credentials or tokens.

## Build locally

From the repository root:

```bash
python -m pip install build twine
python -m build
twine check dist/*
```

Expected result: wheel and source distribution are created under `dist/`, and `twine check` passes.

## Test install the wheel locally

```bash
python -m venv /tmp/runtrace-wheel-test
source /tmp/runtrace-wheel-test/bin/activate
pip install dist/*.whl
runtrace demo
```

Optional extra checks:

```bash
runtrace --help
python -m runtrace --help
runtrace index
runtrace export --output summary.json
python -m json.tool summary.json >/dev/null
```

## Publish later manually

Only run this after the release checklist passes and PyPI credentials/trusted publishing are configured outside the repository:

```bash
twine upload dist/*
```

Do not commit PyPI credentials, API tokens, `.pypirc`, or environment files.

## Package metadata checklist

Before publishing, verify:

- `README.md` renders correctly as the long description.
- `pyproject.toml` has the correct version.
- `src/runtrace/__init__.py` has the same version.
- project URLs point to the public GitHub repository.
- templates are included in the wheel.
- a clean wheel install can run `runtrace demo` and generate reports.
