from __future__ import annotations

import os
import pty
import select
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], cwd: Path, output_log: Path, use_pty: bool | None = None) -> int:
    if not command:
        raise ValueError("No command provided after --")
    output_log.parent.mkdir(parents=True, exist_ok=True)
    if use_pty is None:
        use_pty = sys.stdin.isatty() and os.name == "posix"
    if use_pty:
        return _run_with_pty(command, cwd, output_log)
    return _run_with_subprocess(command, cwd, output_log)


def _run_with_subprocess(command: list[str], cwd: Path, output_log: Path) -> int:
    with output_log.open("w", encoding="utf-8", errors="replace") as log:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log.write(line)
            log.flush()
        return process.wait()


def _run_with_pty(command: list[str], cwd: Path, output_log: Path) -> int:
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(cwd)
        os.execvp(command[0], command)
    with output_log.open("wb") as log:
        while True:
            ready, _, _ = select.select([fd], [], [], 0.1)
            if fd in ready:
                try:
                    data = os.read(fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                os.write(sys.stdout.fileno(), data)
                log.write(data)
                log.flush()
            try:
                waited_pid, status = os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                break
            if waited_pid == pid:
                if os.WIFEXITED(status):
                    return os.WEXITSTATUS(status)
                if os.WIFSIGNALED(status):
                    return 128 + os.WTERMSIG(status)
                return status
    _, status = os.waitpid(pid, 0)
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)
    if os.WIFSIGNALED(status):
        return 128 + os.WTERMSIG(status)
    return status
