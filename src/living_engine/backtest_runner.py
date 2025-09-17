"""Utilities for running simple backtests against Living Engine strategies."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .strategy_api import Capsule, StrategyBase


class BacktestRunner:
    """Execute a single-pass backtest and summarize the results."""

    def __init__(self, config: Dict[str, Any], data: pd.DataFrame):
        self.config = config
        self._backtest_cfg = config.get("backtest", {})
        self.data = self._prepare_data(data)
        self.strategy = self._build_strategy(config.get("strategy", {}))

    # ------------------------------------------------------------------
    def _prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")
        timestamp_col = self._backtest_cfg.get("timestamp_column", "timestamp")
        if timestamp_col not in data.columns:
            raise ValueError(f"Missing required column: {timestamp_col}")

        frame = data.copy()
        frame[timestamp_col] = pd.to_datetime(frame[timestamp_col], errors="coerce")
        frame = frame.dropna(subset=[timestamp_col])
        frame = frame.sort_values(timestamp_col).reset_index(drop=True)
        return frame

    def _build_strategy(self, strategy_cfg: Dict[str, Any]) -> StrategyBase:
        module_name = strategy_cfg.get("module", "living_engine.imm_core")
        class_name = strategy_cfg.get("class", "ImmCore")
        params = strategy_cfg.get("params", {})

        module = import_module(module_name)
        try:
            strategy_cls = getattr(module, class_name)
        except AttributeError as exc:  # pragma: no cover - configuration error
            raise ImportError(f"Strategy class '{class_name}' not found in '{module_name}'.") from exc

        strategy = strategy_cls(params)
        if not isinstance(strategy, StrategyBase):  # pragma: no cover - defensive
            raise TypeError("Strategy must inherit from StrategyBase.")
        return strategy

    # ------------------------------------------------------------------
    def run(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Run the backtest and return a blotter plus a proof capsule summary."""

        timestamp_col = self._backtest_cfg.get("timestamp_column", "timestamp")
        price_col = self._backtest_cfg.get("price_column", "close")
        claim = self._backtest_cfg.get("claim", "P≠NP")

        blotter_records: List[Dict[str, Any]] = []
        capsule_log: List[Capsule] = []
        entry_time: Optional[Any] = None
        entry_price: Optional[float] = None
        final_verdict = "INCONCLUSIVE"

        self.strategy.on_start()
        for _, row in self.data.iterrows():
            bar = row.to_dict()
            order, capsule = self.strategy.on_bar(bar)

            if capsule:
                capsule_log.append(capsule)
                verdict = capsule.get("verdict")
                if verdict:
                    final_verdict = verdict

            if order:
                side = order.get("side")
                if side == "long":
                    entry_time = bar.get(timestamp_col)
                    price = bar.get(price_col)
                    entry_price = float(price) if price is not None else None
                elif side == "flat" and entry_time is not None and entry_price is not None:
                    exit_time = bar.get(timestamp_col)
                    price = bar.get(price_col, entry_price)
                    exit_price = float(price) if price is not None else entry_price
                    pnl = exit_price - entry_price
                    blotter_records.append(
                        {
                            "entry_time": entry_time,
                            "exit_time": exit_time,
                            "pnl": pnl,
                        }
                    )
                    entry_time = None
                    entry_price = None

        self.strategy.on_finish()

        blotter = pd.DataFrame(blotter_records, columns=["entry_time", "exit_time", "pnl"])

        def _serialize_timestamp(value: Any) -> Any:
            if hasattr(value, "isoformat"):
                return value.isoformat()
            return value

        entropy_trace: List[Dict[str, Any]] = [
            {
                "timestamp": _serialize_timestamp(capsule.get("timestamp")),
                "entropy": capsule.get("entropy"),
                "regime": capsule.get("regime"),
            }
            for capsule in capsule_log
        ]
        capsule_summary = {
            "claim": claim,
            "verdict": final_verdict,
            "entropy_trace": entropy_trace,
        }
        return blotter, capsule_summary


__all__ = ["BacktestRunner"]
