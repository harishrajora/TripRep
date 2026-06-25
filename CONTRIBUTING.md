# Contributing to TripRep

Thanks for your interest in improving TripRep! This guide explains how to set up the
project, propose changes, and get them merged.

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to Contribute

- Report bugs and request features via [GitHub Issues](https://github.com/harishrajora/TripRep/issues)
- Improve documentation (README, this guide, in-code comments)
- Fix bugs or build new features
- Review open pull requests

## Development Setup

TripRep is a Django app. See the [README](README.md) for full details; the short version:

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/TripRep.git
cd TripRep

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables (.env in the project root)
echo "genai_api_key=YOUR_GOOGLE_GENAI_API_KEY" > .env

# 5. Apply migrations and run
python manage.py migrate
python manage.py runserver
```

> A default local superuser (`hrajora` / `hrajora`) is auto-created by `core/signals.py`
> for development only. Never rely on it outside local testing.

## Branching and Workflow

1. Create a focused feature branch off `main`:
   ```bash
   git checkout -b fix/short-description
   ```
2. Make small, self-contained changes.
3. Keep commits clear and scoped to one logical change.
4. Push your branch and open a pull request against `main`.

## Before You Open a Pull Request

Please make sure your change:

- [ ] Runs `python manage.py check` cleanly (no new errors)
- [ ] Includes a migration if you changed any model (`python manage.py makemigrations`)
- [ ] Does not commit secrets, `db.sqlite3`, `.env`, or files under `media/`
- [ ] Follows the existing code and template style
- [ ] Updates the README or docs if behavior or routes changed
- [ ] Has a clear PR description explaining what changed and why

## Coding Guidelines

- **Python**: follow [PEP 8](https://peps.python.org/pep-0008/); keep functions small and readable.
- **Templates**: match the structure and CSS classes already used in `core/templates/core/`.
- **Frontend**: reuse existing styles in `core/static/core/css/style.css` rather than adding one-off styles.
- **Logging**: prefer real logging over `print` statements in new code.
- **No new dependencies** without calling them out clearly in the PR (and adding them to `requirements.txt`).

## Reporting Bugs and Requesting Features

Use the issue templates under [New Issue](https://github.com/harishrajora/TripRep/issues/new/choose).
A good bug report includes steps to reproduce, expected vs. actual behavior, and environment details.

## Security Issues

Please do **not** open public issues for security vulnerabilities.
See [SECURITY.md](SECURITY.md) for how to report them privately.

## Questions

Open a [discussion or issue](https://github.com/harishrajora/TripRep/issues) and we'll help out.
Thanks for contributing! 🧳
