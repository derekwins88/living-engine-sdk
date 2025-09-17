"""Strategy primitives used throughout the SDK."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

BarData = Dict[str, Any]
Order = Dict[str, Any]
Capsule = Dict[str, Any]


class StrategyBase:
    """Minimal interface for Living Engine strategies.

    Subclasses should override the lifecycle hooks (`on_start`, `on_finish`, and `on_bar`).
    The default implementation only stores the provided `params` dictionary and exposes a
    mutable `state` dictionary for strategy-specific bookkeeping.
    """

    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.state: Dict[str, Any] = {}

    def on_start(self) -> None:
        """Called before the first bar is processed."""

    def on_finish(self) -> None:
        """Called after the final bar is processed."""

    def on_bar(self, bar: BarData) -> Tuple[Optional[Order], Optional[Capsule]]:
        """Process a bar of data.

        Parameters
        ----------
        bar:
            A dictionary containing the minimum keys required by the strategy implementation
            (typically a timestamp, close price, and entropy score).

        Returns
        -------
        Tuple[Optional[Order], Optional[Capsule]]
            A tuple containing the next order (or ``None``) and an optional capsule dictionary.
        """

        raise NotImplementedError


__all__ = [
    "BarData",
    "Capsule",
    "Order",
    "StrategyBase",
]
