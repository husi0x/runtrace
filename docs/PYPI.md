# PyPI release maintenance

Runtrace is published on PyPI:

```text
https://pypi.org/project/runtrace/
```

Public install command:

```bash
pipx install runtrace
```

`pipx` is recommended for CLI usage because it installs Runtrace into an isolated environment and exposes the `runtrace` command.

## Build a future release

From the repository root:

```bash
python -m pip install build twine
rm -rf dist build *.egg-info
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

## Upload a future release manually

Only run this after the release checklist passes and PyPI credentials or trusted publishing are configured outside the repository:

```bash
twine upload dist/*
```

The first release already exists, so future API tokens should preferably be project-scoped to `runtrace`.

Do not commit PyPI credentials, API tokens, `.pypirc`, or environment files.

## Package metadata checklist

Before uploading a future release, verify:

- `README.md` renders correctly as the long description.
- `pyproject.toml` has the correct version.
- `src/runtrace/__init__.py` has the same version.
- project URLs point to the public GitHub repository.
- templates are included in the wheel.
- a clean wheel install can run `runtrace demo` and generate reports.
