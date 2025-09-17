"""Narrative helpers for summarising daily activity."""

from __future__ import annotations

from typing import Mapping


def make_day_summary(
    metrics: Mapping[str, float],
    proofbridge_stats: Mapping[str, int],
    verdict: str,
) -> str:
    """Compose a human-readable summary for the trading day."""

    sharpe = metrics.get("sharpe", 0.0)
    max_drawdown = metrics.get("max_drawdown", 0.0)
    num_trades = int(metrics.get("num_trades", 0))
    final_equity = metrics.get("final_equity", 0.0)
    capsules = proofbridge_stats.get("capsules_written", 0)

    mood = "confident" if max_drawdown <= 0.15 else "cautious"
    return (
        "Day Summary — The Engine felt {mood}.\n"
        "Sharpe: {sharpe:.2f}  MaxDD: {max_dd:.2%}  Trades: {trades}  FinalEquity: {equity:.2f}\n"
        "Verdict: {verdict} (capsules: {capsules})\n"
    ).format(
        mood=mood,
        sharpe=sharpe,
        max_dd=max_drawdown,
        trades=num_trades,
        equity=final_equity,
        verdict=verdict,
        capsules=capsules,
    )


__all__ = ["make_day_summary"]
