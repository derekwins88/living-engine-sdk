"""Minimal runnable sample for the Living Engine SDK."""

from __future__ import annotations

from pathlib import Path

from living_engine import ImmCore, ProofBridge, make_day_summary, sha256_file

PARAMS = {
    "entropy": {"P_threshold": 0.045, "NP_threshold": 0.09, "CollapseThreshold": 0.12},
    "signals": {"EmaFast": 12, "EmaSlow": 30},
}

BARS = [
    {"timestamp": "t0", "close": 75.20, "entropy": 0.038},
    {"timestamp": "t1", "close": 75.48, "entropy": 0.052},
    {"timestamp": "t2", "close": 75.22, "entropy": 0.067},
    {"timestamp": "t3", "close": 74.98, "entropy": 0.072},
    {"timestamp": "t4", "close": 74.72, "entropy": 0.13},
]


def main() -> None:
    output_dir = Path("example_output")
    output_dir.mkdir(exist_ok=True)

    strategy = ImmCore(PARAMS)
    strategy.on_start()

    with ProofBridge(output_dir / "ledger.csv", output_dir / "capsules.jsonl") as bridge:
        for bar in BARS:
            order, capsule = strategy.on_bar(bar)
            if order:
                print(f"Order emitted: {order}")
            if capsule:
                bridge.write_capsule(bar["timestamp"], capsule)

        metrics = {
            "sharpe": 0.0,
            "max_drawdown": 0.05,
            "num_trades": 2,
            "final_equity": 50_000,
        }
        summary = make_day_summary(metrics, bridge.stats(), "P≠NP (claim)")
        (output_dir / "summary.txt").write_text(summary, encoding="utf-8")
        print(summary)

    print("Ledger SHA-256:", sha256_file(output_dir / "ledger.csv"))


if __name__ == "__main__":
    main()
