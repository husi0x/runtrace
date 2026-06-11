from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from runtrace import __version__
from runtrace.paths import relative_to_cwd, run_dir
from runtrace.recorder import (
    delete_old_runs,
    list_runs,
    load_metadata,
    record_run,
    resolve_run_id,
)
from runtrace.reports import build_report_summary, generate_reports

app = typer.Typer(
    help="Runtrace — a black box for AI coding agents.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


def _print_error(message: str, next_step: str | None = None) -> None:
    body = f"[red]{message}[/red]"
    if next_step:
        body += f"\n\n[bold]Try:[/bold] {next_step}"
    console.print(Panel(body, title="Runtrace", border_style="red"))


def _print_paths(title: str, run_id: str, paths: list[Path]) -> None:
    output_log = run_dir(Path.cwd(), run_id) / "output.log"
    lines = [f"[bold]Run ID:[/bold] {run_id}", "", "[bold]Report:[/bold]"]
    for path in paths:
        label = "Markdown" if path.suffix == ".md" else "HTML"
        lines.append(f"  {label + ':':9} {relative_to_cwd(path)}")
    lines.append(f"  {'Output:':9} {relative_to_cwd(output_log)}")
    lines.extend(
        [
            "",
            "[bold]Next:[/bold]",
            f"  runtrace show {run_id}",
            f"  xdg-open {relative_to_cwd(run_dir(Path.cwd(), run_id) / 'report.html')}",
        ]
    )
    console.print(Panel("\n".join(lines), title=title, border_style="green"))


@app.callback()
def main() -> None:
    """Record, inspect, and report local command runs."""


@app.command("version")
def version_cmd() -> None:
    """Print the installed Runtrace version."""
    console.print(f"Runtrace {__version__}")


@app.command("demo")
def demo_cmd() -> None:
    """Record a safe demo run and generate Markdown + HTML reports."""
    command = [
        sys.executable,
        "-c",
        "print('Runtrace demo')\nprint('This command is safe and local.')\nprint('Open the HTML report next.')",
    ]
    metadata = record_run(command, Path.cwd(), name="Runtrace demo", use_pty=False)
    paths = generate_reports(Path.cwd(), metadata.run_id, "both")
    _print_paths("Runtrace demo complete", metadata.run_id, paths)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(
    ctx: typer.Context,
    name: Annotated[str | None, typer.Option("--name", "-n", help="Human-readable run name.")] = None,
) -> None:
    """Record any command.

    Put -- before the command you want to run.

    Examples:
      runtrace run --name "tests" -- pytest -q
      runtrace run --name "codex bugfix" -- codex exec "fix failing tests"
    """
    command = list(ctx.args)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        _print_error("No command was provided after --.", "runtrace run -- python -c \"print('hello')\"")
        raise typer.Exit(2)

    try:
        metadata = record_run(command, Path.cwd(), name=name)
    except FileNotFoundError:
        _print_error(f"Command not found: {command[0]}", "check the command name or use runtrace demo")
        raise typer.Exit(127) from None

    if not metadata.git_after.git_available:
        console.print(
            "[yellow]This directory is not a git repository. Runtrace will still record command output, "
            "but git diff tracking is disabled.[/yellow]"
        )

    status = "success" if metadata.succeeded else "failed"
    color = "green" if metadata.succeeded else "red"
    run_folder = relative_to_cwd(run_dir(Path.cwd(), metadata.run_id))
    message = (
        f"[bold]Run ID:[/bold] {metadata.run_id}\n"
        f"[bold]Status:[/bold] [{color}]{status}[/]\n"
        f"[bold]Exit code:[/bold] {metadata.exit_code}\n"
        f"[bold]Run folder:[/bold] {run_folder}\n\n"
        f"[bold]Next:[/bold]\n"
        f"  runtrace report --run-id {metadata.run_id}\n"
        f"  runtrace show {metadata.run_id}"
    )
    if not metadata.succeeded:
        message += f"\n\n[yellow]Command exited with code {metadata.exit_code}. The run was recorded anyway.[/]"
    console.print(Panel(message, title="Runtrace run recorded", border_style=color))
    raise typer.Exit(metadata.exit_code or 0)


@app.command("report")
def report_cmd(
    run_id: Annotated[str | None, typer.Option("--run-id", help="Run ID to report. Defaults to latest.")] = None,
    fmt: Annotated[str, typer.Option("--format", "-f", help="md, html, or both")] = "both",
) -> None:
    """Generate Markdown and/or HTML reports for a run."""
    try:
        paths = generate_reports(Path.cwd(), run_id, fmt)
    except FileNotFoundError:
        _print_error("No runs found yet.", "runtrace demo")
        raise typer.Exit(1) from None
    except ValueError as exc:
        _print_error(str(exc), "runtrace report --format both")
        raise typer.Exit(2) from None

    actual_id = resolve_run_id(Path.cwd(), run_id)
    assert actual_id is not None
    _print_paths("Runtrace report generated", actual_id, paths)


def _render_runs_table() -> None:
    runs = list_runs(Path.cwd())
    if not runs:
        console.print("[yellow]No runs found yet. Try: runtrace demo[/yellow]")
        return
    table = Table(title="Runtrace runs")
    for col in ("run_id", "name", "command", "result", "duration", "created", "changed"):
        table.add_column(col)
    for item in runs:
        table.add_row(
            item.run_id,
            item.name,
            item.command_shell,
            "success" if item.succeeded else "failed",
            f"{item.duration_seconds}s",
            item.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            str(len(item.changed_files)),
        )
    console.print(table)


@app.command("list")
def list_cmd() -> None:
    """List recent runs, newest first."""
    _render_runs_table()


@app.command("runs")
def runs_cmd() -> None:
    """Alias for runtrace list."""
    _render_runs_table()


def _show_run(run_id: str) -> None:
    actual_id = resolve_run_id(Path.cwd(), run_id)
    if not actual_id:
        _print_error("No runs found yet.", "runtrace demo")
        raise typer.Exit(1)
    try:
        metadata = load_metadata(Path.cwd(), actual_id)
    except FileNotFoundError:
        _print_error(f"Run not found: {run_id}", "runtrace list")
        raise typer.Exit(1) from None

    summary = build_report_summary(metadata)
    report_md = run_dir(Path.cwd(), metadata.run_id) / "report.md"
    report_html = run_dir(Path.cwd(), metadata.run_id) / "report.html"

    status = "success" if metadata.succeeded else "failed"
    color = "green" if metadata.succeeded else "red"
    console.print(
        Panel.fit(
            f"[bold]{metadata.name}[/bold]\n"
            f"Run ID: {metadata.run_id}\n"
            f"Status: [{color}]{status}[/] / exit {metadata.exit_code}\n"
            f"Duration: {metadata.duration_seconds}s\n"
            f"Command: [cyan]{metadata.command_shell}[/cyan]\n"
            f"Changed files: {len(metadata.changed_files)}",
            title="Runtrace run",
            border_style=color,
        )
    )

    if metadata.changed_files:
        table = Table(title="Changed files")
        table.add_column("path")
        for path in metadata.changed_files[:20]:
            table.add_row(path)
        console.print(table)

    checklist = Table(title="Review checklist")
    checklist.add_column("check")
    checklist.add_column("result")
    checklist.add_column("notes")
    for finding in summary.findings:
        checklist.add_row(finding.title, finding.status, finding.detail)
    console.print(checklist)

    if not report_md.exists() or not report_html.exists():
        console.print(
            f"[yellow]No report exists for this run yet. Generate one with: "
            f"runtrace report --run-id {metadata.run_id}[/yellow]"
        )
    else:
        console.print(f"Report: {relative_to_cwd(report_html)}")


@app.command("show")
def show_cmd(run_id: str) -> None:
    """Show one run in the terminal. Use 'latest' for the newest run."""
    _show_run(run_id)


@app.command("latest")
def latest_cmd() -> None:
    """Show the latest run."""
    _show_run("latest")


@app.command("clean")
def clean_cmd(
    keep: Annotated[int, typer.Option("--keep", help="Number of newest runs to keep.")] = 20,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation.")] = False,
) -> None:
    """Delete old run folders."""
    runs = list_runs(Path.cwd())
    doomed = max(0, len(runs) - keep)
    if doomed == 0:
        console.print("Nothing to clean.")
        return
    if not yes and not typer.confirm(f"Delete {doomed} old Runtrace run folder(s)?"):
        console.print("Cancelled.")
        return
    removed = delete_old_runs(Path.cwd(), keep=keep)
    console.print(f"[green]Deleted {len(removed)} run folder(s).[/green]")


if __name__ == "__main__":
    app()
