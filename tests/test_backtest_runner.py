from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import pytest
import yaml

from living_engine.backtest_runner import BacktestRunner


def _read_yaml(p: Path) -> dict:
    with open(p, "r") as f:
        return yaml.safe_load(f)


def _read_csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p, parse_dates=["timestamp"])


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_backtest_runs_and_emits_artifacts(tmp_path: Path) -> None:
    """Smoke test: run one pass and validate blotter + capsule structure."""
    cfg_path = Path(os.environ.get("LE_CONFIG_PATH", "config/default.yaml"))
    csv_path = Path(os.environ.get("LE_DATA_PATH", "data/sample.csv"))
    assert cfg_path.exists(), "missing config/default.yaml"
    assert csv_path.exists(), "missing data/sample.csv"

    config = _read_yaml(cfg_path)
    data = _read_csv(csv_path)

    runner = BacktestRunner(config=config, frame=data)
    artifacts = runner.run(outdir=tmp_path)

    # Files should exist
    for key in ["blotter", "capsule", "metrics", "summary"]:
        assert key in artifacts
        assert Path(artifacts[key]).exists(), f"{key} not written"

    # Blotter sanity
    blotter = pd.read_csv(artifacts["blotter"])
    assert set({"ts", "action", "px", "size"}).issubset(blotter.columns)
    # Either we traded, or we cleanly chose not to; both are valid. Just ensure schema is OK.
    assert blotter.dtypes["px"].kind in ("f", "i")

    # Capsule sanity
    capsule = json.loads(Path(artifacts["capsule"]).read_text())
    for k in ["schema_version", "verdict", "params", "metrics", "evidence", "data_sha256"]:
        assert k in capsule
