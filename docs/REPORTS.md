# Runtrace reports

Runtrace stores data locally in `.runtrace/` inside the directory where you ran it.

```text
.runtrace/runs/<run_id>/
├── metadata.json
├── output.log
├── report.md
└── report.html
```

## Where reports live

Reports are written into the run folder:

```text
.runtrace/runs/<run_id>/report.md
.runtrace/runs/<run_id>/report.html
```

Generate them with:

```bash
runtrace report
runtrace report --run-id <run_id>
```

## What metadata is recorded

`metadata.json` contains:

- run ID and run name
- working directory
- command as a list
- command as a shell string
- start time and end time
- duration in seconds
- exit code
- success/failure status
- output log path
- output preview
- git snapshot before the command
- git snapshot after the command
- changed files
- added/modified/deleted file lists when detectable from git status
- diff stat
- full git diff when available
- whether the working tree changed

## Markdown report

`report.md` is designed for quick review in editors, terminals, PR comments, and notes.

Sections:

- Header
- Summary
- Command
- Git state
- Changed files
- Diff stat
- Review checklist
- Output log
- Metadata

## HTML report

`report.html` is a self-contained dark report. It uses no CDN and no external assets.

It includes:

- run summary cards
- status badges
- command block
- git state
- changed file list
- review checklist
- diff stat
- output preview
- link to `output.log`

The HTML report intentionally does not embed huge full diffs or huge full command output by default. Use `metadata.json` and `output.log` for the full record.

## How the checklist works

The review checklist is deterministic. It uses simple string/path heuristics. No LLM calls are made.

Checks include:

- command completed successfully
- command failed
- tests detected from command/output
- tests likely passed
- tests likely failed
- sensitive files touched
- dependency/config files touched
- large diff warning
- no git repo warning

## What “Unknown” means

`Unknown` means Runtrace did not find enough signal to make a confident call.

Example: if the command was `python script.py`, Runtrace does not assume tests ran. It marks test status as unknown instead of pretending.

## Privacy note

Runtrace stores data locally in `.runtrace/`.

It does not call network APIs. It does not call LLM APIs. It does not upload reports.

Be aware that `output.log`, `metadata.json`, and reports can contain command output and file paths from your machine. Do not commit `.runtrace/` unless you intentionally want to share those records.
