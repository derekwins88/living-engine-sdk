from __future__ import annotations

import json
import os

import pandas as pd
import pytest
import yaml

from living_engine.backtest_runner import BacktestRunner
import os
import json
import yaml
import pandas as pd

from living_engine.backtest_runner import BacktestRunner

CFG_PATH = os.path.join("config", "default.yaml")
CSV_PATH = os.path.join("data", "sample.csv")

def load_config():
    with open(CFG_PATH, "r") as f:
        return yaml.safe_load(f)

def load_data():
    return pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

def test_backtest_runs_and_outputs(tmp_path):
    config = load_config()
    data = load_data()

    runner = BacktestRunner(config, data)
    blotter, capsule = runner.run()

    # --- Blotter assertions ---
    assert isinstance(blotter, pd.DataFrame)
    assert "entry_time" in blotter.columns
    assert "exit_time" in blotter.columns
    assert "pnl" in blotter.columns

    # --- Capsule assertions ---
    assert isinstance(capsule, dict)
    assert "claim" in capsule
    assert "verdict" in capsule
    assert "entropy_trace" in capsule

    # --- Export check ---
    out_file = tmp_path / "capsule.json"
    with open(out_file, "w") as f:
        json.dump(capsule, f, indent=2)

    assert out_file.exists()
