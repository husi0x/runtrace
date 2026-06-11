# Runtrace configuration

Runtrace works without configuration. If `.runtrace/config.toml` exists, Runtrace uses it to tune the deterministic review checklist.

Create the default config:

```bash
runtrace init
```

Overwrite an existing config:

```bash
runtrace init --force
```

Default config:

```toml
[review]
large_diff_file_limit = 20
sensitive_patterns = [
  ".env",
  "secret",
  "token",
  "credential",
  "password",
  "auth",
  "login",
  "session",
  "jwt",
  "oauth",
  "config",
  "settings",
]
dependency_patterns = [
  "package.json",
  "package-lock.json",
  "pnpm-lock.yaml",
  "yarn.lock",
  "pyproject.toml",
  "requirements.txt",
  "uv.lock",
  "poetry.lock",
  "Dockerfile",
  "docker-compose.yml",
  ".github/workflows",
]
test_commands = [
  "pytest",
  "unittest",
  "npm test",
  "pnpm test",
  "yarn test",
  "vitest",
  "jest",
  "cargo test",
  "go test",
]
```

## Rules

- `large_diff_file_limit`: warns when more than this many files changed or the diff stat suggests more than this many changed files.
- `sensitive_patterns`: path substrings that trigger the sensitive-files warning.
- `dependency_patterns`: path substrings that trigger dependency/config warnings.
- `test_commands`: command/output substrings used to detect whether tests likely ran.

Malformed config files never crash Runtrace. It prints a warning and uses built-in defaults.

The config is local to a project and lives in `.runtrace/config.toml`.
