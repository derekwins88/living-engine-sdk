# living-engine-sdk (umbrella)

This repository now acts as an umbrella for the Living Engine platform. The Python SDK lives in
`packages/sdk`, and optional companion projects (such as the backtest harness) can be attached under
`packages/` as git submodules.

## Repository layout
```
living-engine-sdk/
├─ packages/
│  ├─ sdk/         # main Python SDK (installable package, tests, examples)
│  └─ backtest/    # optional submodule → live-living-engine-backtest
├─ docs/           # architecture overview + capsule schema references
└─ .github/        # CI configuration
```

## Get started
```bash
git clone https://github.com/your-org/living-engine-sdk
cd living-engine-sdk
pip install pre-commit
pre-commit install

cd packages/sdk
pip install -e .
pytest
```

## Add the backtest harness (optional)
```bash
git submodule add https://github.com/<you>/live-living-engine-backtest packages/backtest
git commit -m "chore: add backtest submodule"
```

With the submodule attached, CI will run the harness' smoke scenario using the bundled sample
configuration and CSV. The job expects the script to emit a `metrics.json` artifact.

## CI summary
- **`sdk-tests`** installs the SDK from `packages/sdk`, runs pre-commit, and executes `pytest`.
- **`backtest-smoke`** runs only when `packages/backtest` exists and verifies that the harness can
  produce proof artifacts from its default sample data.

For more platform context, see [`docs/overview.md`](docs/overview.md) and the capsule schema in
[`docs/capsule_schema.md`](docs/capsule_schema.md).
