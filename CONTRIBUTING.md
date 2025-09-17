# Contributing to living-engine-sdk

Thanks for your interest in improving the Living Engine SDK! This document captures the
recommended workflow when contributing changes.

## Getting started

```bash
git clone https://github.com/your-org/living-engine-sdk.git
cd living-engine-sdk
python -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -U pip pytest pre-commit
pre-commit install
```

## Development workflow

- Create feature branches from `main`.
- Run `pytest` and `pre-commit run --all-files` before pushing.
- Update documentation, examples, and changelog entries when behavior changes.
- Keep pull requests focused and describe the motivation clearly in the PR template.

## Reporting issues

Use the built-in issue templates where possible. Include reproduction steps, expected versus
actual results, and environment information (Python version, OS, etc.).

## Releases

- Bump the version in `pyproject.toml`.
- Add a new section to `CHANGELOG.md` summarizing the release.
- Tag the release in Git (`git tag -a vX.Y.Z -m "vX.Y.Z"`).
