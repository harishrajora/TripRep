# Security Policy

## Reporting a Vulnerability

Please **do not report security vulnerabilities through public GitHub issues**,
discussions, or pull requests.

Instead, report them privately using GitHub's
[private vulnerability reporting](https://github.com/harishrajora/TripRep/security/advisories/new).
This keeps the details confidential until a fix is available.

When reporting, please include as much of the following as you can:

- A description of the vulnerability and its impact
- Steps to reproduce, or a proof-of-concept
- Affected route, view, or file (if known)
- Any suggested remediation

We will acknowledge your report, investigate, and keep you informed of progress
toward a fix. Please give us a reasonable amount of time to address the issue
before any public disclosure.

## Scope

TripRep is currently in active development and is intended primarily for local
and demonstration use. Note that the default configuration is **not** hardened
for production. In particular:

- `DEBUG = True` and a placeholder `SECRET_KEY` ship in `TripRep/settings.py`
- A default superuser (`hrajora` / `hrajora`) is auto-created by `core/signals.py`
- SQLite is used as the default database

These are documented in the README's "Production and Security Notes" and must be
changed before any public deployment. Reports about these known development
defaults are appreciated but already tracked.

## Supported Versions

As a pre-release project, only the latest `main` branch is supported. Please
ensure you are on the most recent commit before reporting an issue.
