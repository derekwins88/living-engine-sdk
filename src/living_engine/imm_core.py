"""Reference implementation of a simple entropy-aware strategy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple

from .entropy import classify_regime
from .strategy_api import BarData, Capsule, Order, StrategyBase


def _ema(previous: Optional[float], price: float, period: int) -> float:
    """Compute an exponential moving average."""

    if period <= 1 or previous is None:
        return price
    alpha = 2.0 / (period + 1.0)
    return alpha * price + (1.0 - alpha) * previous


@dataclass(frozen=True)
class _EntropyConfig:
    p_threshold: float
    np_threshold: float
    collapse_threshold: float

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "_EntropyConfig":
        try:
            return cls(
                p_threshold=float(data["P_threshold"]),
                np_threshold=float(data["NP_threshold"]),
                collapse_threshold=float(data["CollapseThreshold"]),
            )
        except KeyError as exc:  # pragma: no cover - defensive configuration error
            raise ValueError(f"Missing entropy parameter: {exc.args[0]}") from exc


@dataclass(frozen=True)
class _SignalConfig:
    fast_period: int
    slow_period: int

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "_SignalConfig":
        try:
            fast = int(data["EmaFast"])
            slow = int(data["EmaSlow"])
        except KeyError as exc:  # pragma: no cover - defensive configuration error
            raise ValueError(f"Missing signal parameter: {exc.args[0]}") from exc

        if fast <= 0 or slow <= 0:
            raise ValueError("EMA periods must be positive integers.")
        if fast >= slow:
            raise ValueError("Fast EMA period must be shorter than slow EMA period.")
        return cls(fast_period=fast, slow_period=slow)


class ImmCore(StrategyBase):
    """A deterministic strategy that reacts to entropy regimes.

    The strategy attempts to remain long when the regime is ``P-like`` **and** the fast EMA
    exceeds the slow EMA. It flattens positions when entropy migrates into ``NP`` territory or
    when the EMA crossover reverses. Any collapse regime produces a proof capsule asserting the
    ``P≠NP`` claim.
    """

    def __init__(self, params: Dict[str, Any]):
        super().__init__(params)
        self._entropy_cfg = _EntropyConfig.from_mapping(params.get("entropy", {}))
        self._signal_cfg = _SignalConfig.from_mapping(params.get("signals", {}))
        self._reset_state()

    # ------------------------------------------------------------------
    # lifecycle hooks
    def _reset_state(self) -> None:
        self.state.update({"ema_fast": None, "ema_slow": None, "position": 0})

    def on_start(self) -> None:
        self._reset_state()

    def on_finish(self) -> None:  # pragma: no cover - hook for future use
        """Finalize resources. Currently a no-op."""

    # ------------------------------------------------------------------
    def on_bar(self, bar: BarData) -> Tuple[Optional[Order], Optional[Capsule]]:
        timestamp = bar.get("timestamp")
        price = float(bar["close"])
        entropy_value = float(bar.get("entropy", 0.0))

        # Update moving averages.
        self.state["ema_fast"] = _ema(self.state.get("ema_fast"), price, self._signal_cfg.fast_period)
        self.state["ema_slow"] = _ema(self.state.get("ema_slow"), price, self._signal_cfg.slow_period)

        regime = classify_regime(
            entropy_value,
            self._entropy_cfg.p_threshold,
            self._entropy_cfg.np_threshold,
            self._entropy_cfg.collapse_threshold,
        )

        order: Optional[Order] = None
        capsule: Optional[Capsule] = None
        capsule_payload: Capsule = {
            "timestamp": timestamp,
            "glyph": regime["glyph"],
            "entropy": regime["entropy"],
            "regime": regime["regime"],
        }

        # Entry condition: long when regime is P-like and fast EMA is above slow EMA.
        if self.state["position"] == 0:
            if regime["regime"] == "P-like" and self.state["ema_fast"] > self.state["ema_slow"]:
                self.state["position"] = 1
                order = {"side": "long", "size": 1, "timestamp": timestamp}
                capsule = {**capsule_payload, "verdict": "OPEN"}

        # Exit conditions: collapse regime, NP regime, or EMA crossover failure.
        else:
            should_flatten = False
            verdict = "FLAT"
            if regime["regime"] in {"NP", "collapse"}:
                should_flatten = True
            elif self.state["ema_fast"] <= self.state["ema_slow"]:
                should_flatten = True
                verdict = "CROSS-DOWN"

            if should_flatten:
                self.state["position"] = 0
                order = {"side": "flat", "size": 0, "timestamp": timestamp}
                capsule = {**capsule_payload, "verdict": verdict}

        if regime["regime"] == "collapse":
            capsule = {**capsule_payload, "verdict": "P≠NP (claim)"}

        return order, capsule


__all__ = ["ImmCore"]
