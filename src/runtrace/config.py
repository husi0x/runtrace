from __future__ import annotations

import sys
import tomllib
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from runtrace.paths import runtrace_dir

DEFAULT_SENSITIVE_PATTERNS = [
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
DEFAULT_DEPENDENCY_PATTERNS = [
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
DEFAULT_TEST_COMMANDS = [
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


class ReviewConfig(BaseModel):
    large_diff_file_limit: int = 20
    sensitive_patterns: list[str] = Field(default_factory=lambda: DEFAULT_SENSITIVE_PATTERNS.copy())
    dependency_patterns: list[str] = Field(default_factory=lambda: DEFAULT_DEPENDENCY_PATTERNS.copy())
    test_commands: list[str] = Field(default_factory=lambda: DEFAULT_TEST_COMMANDS.copy())


DEFAULT_CONFIG_TOML = """[review]
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
"""


def config_path(cwd: str | Path = ".") -> Path:
    return runtrace_dir(cwd) / "config.toml"


def default_review_config() -> ReviewConfig:
    return ReviewConfig()


def load_review_config(cwd: str | Path = ".") -> ReviewConfig:
    path = config_path(cwd)
    if not path.exists():
        return default_review_config()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        review_data = data.get("review", {})
        return ReviewConfig.model_validate(review_data)
    except (OSError, tomllib.TOMLDecodeError, ValidationError, TypeError, ValueError) as exc:
        print(f"Runtrace warning: could not read {path}: {exc}. Using built-in review defaults.", file=sys.stderr)
        return default_review_config()


def write_default_config(cwd: str | Path = ".", force: bool = False) -> tuple[Path, bool]:
    path = config_path(cwd)
    if path.exists() and not force:
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEFAULT_CONFIG_TOML, encoding="utf-8")
    return path, True
