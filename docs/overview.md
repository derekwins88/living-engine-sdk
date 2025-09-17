# Living Engine SDK Umbrella Overview

This repository acts as an umbrella for the Living Engine platform. It contains the Python SDK
under `packages/sdk` and leaves room for companion projects (for example the backtest harness)
under `packages/` as git submodules. The goal is to standardize the developer workflow across
all tooling that powers the platform's research loop.

```
living-engine-sdk/
├─ packages/
│  ├─ sdk/         # Python SDK (installable package and tests)
│  └─ backtest/    # optional submodule → live-living-engine-backtest
├─ docs/           # architecture notes and schema references
└─ .github/        # CI configuration
```

The SDK itself is unchanged from the original repository layout; the only difference is that it is
nested below `packages/sdk`. To work on the SDK locally you can run:

```bash
cd packages/sdk
pip install -e .
pytest
```

When a backtest harness is attached, the CI workflow will automatically execute its smoke test so
you can verify that sample data produces metrics and proof capsules.
