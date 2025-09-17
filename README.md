# living-engine-sdk

A reusable Python package for the **Living Engine** research project. It ships a small but
cohesive toolkit so you can classify entropy regimes, experiment with deterministic trading
strategies, generate proof capsules, and narrate the resulting session.

## Features

- **Entropy classification** – convert scalar entropy into `P-like`, `NP-drift`, or
  `collapse` regimes with unicode glyphs for quick visualization.
- **Strategy API** – a lightweight interface (`StrategyBase`) that standardizes strategy
  lifecycle hooks.
- **Reference strategy** – `ImmCore` demonstrates how to combine entropy classification with
  classic EMA crossovers.
- **ProofBridge** – writes a CSV ledger and JSONL capsule stream, plus a convenient
  `sha256_file` helper.
- **Narrative helper** – summarize a trading session in a human-readable block of text.

## Installation

```bash
pip install -e .
```

Optional development dependencies:

```bash
pip install -U pip pytest pre-commit
pre-commit install
```

## Quick start

```python
from living_engine.imm_core import ImmCore

params = {
    "entropy": {"P_threshold": 0.045, "NP_threshold": 0.09, "CollapseThreshold": 0.09},
    "signals": {"EmaFast": 12, "EmaSlow": 30},
}

strategy = ImmCore(params)
strategy.on_start()
order, capsule = strategy.on_bar({"timestamp": "t0", "close": 75.2, "entropy": 0.038})
print(order, capsule)
```

See [`examples/run_example.py`](examples/run_example.py) for a runnable script that wires
strategies, the proof bridge, and narrative helper together.

## Development

- Formatters and linters are managed through [`pre-commit`](.pre-commit-config.yaml).
- Tests live in [`tests/`](tests/).
- GitHub Actions run both test and lint steps via [`ci.yml`](.github/workflows/ci.yml).

## License

This project is distributed under the terms of the [MIT License](LICENSE).
