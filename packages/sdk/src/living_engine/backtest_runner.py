from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

from living_engine.imm_core import ImmCore
from living_engine.narrative import make_day_summary
from living_engine.proofbridge import ProofBridge, sha256_file


def _read_yaml(path: Path) -> Dict:
    if yaml is None:
        # ultra-minimal fallback for your default.yaml structure
        out, section = {}, None
        for line in Path(path).read_text().splitlines():
            if not line.strip() or line.strip().startswith("#"):
                continue
            if not line.startswith(" "):
                key = line.split(":", 1)[0].strip()
                out[key] = {}
                section = key
            else:
                kv = line.strip().split(":", 1)
                if len(kv) != 2:
                    continue
                k, v = kv[0], kv[1].strip()
                if v.lower() in ("true", "false"):
                    v = v.lower() == "true"
                else:
                    try:
                        v = float(v) if "." in v else int(v)
                    except Exception:
                        v = v.strip().strip('"').strip("'")
                out[section][k] = v
        return out
    return yaml.safe_load(Path(path).read_text())


def _sharpe(returns) -> float:
    if len(returns) < 2:
        return 0.0
    mu = sum(returns) / len(returns)
    var = sum((x - mu) ** 2 for x in returns) / max(1, len(returns) - 1)
    sd = math.sqrt(var) if var > 0 else 0.0
    return (mu / sd * math.sqrt(252)) if sd > 0 else 0.0


class BacktestRunner:
    """Tiny orchestrator used by tests and examples."""

    def __init__(self, config: Dict, frame):
        self.cfg = config
        self.df = frame.copy()

    @classmethod
    def from_files(cls, cfg_path: str | Path, csv_path: str | Path) -> "BacktestRunner":
        cfg = _read_yaml(Path(cfg_path))
        import pandas as pd

        df = pd.read_csv(csv_path)
        return cls(cfg, df)

    def run(self, outdir: str | Path) -> Dict[str, str]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)

        strat = ImmCore(self.cfg)
        pb = ProofBridge(out / "proof_ledger.csv", out / "capsules.jsonl")

        cash = 50_000.0
        pos = 0
        equity_curve = []
        trades = []
        collapse_hits = 0

        strat.on_start()
        for _, r in self.df.iterrows():
            bar = {
                "timestamp": str(r["timestamp"]),
                "symbol": str(r.get("symbol", "X")),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r["volume"]),
                "entropy": float(r.get("entropy", 0.0)),
            }
            price = bar["close"]
            order, capsule = strat.on_bar(bar)

            if capsule and capsule.get("verdict") == "P≠NP (claim)":
                collapse_hits += 1
            if capsule:
                pb.write_capsule(bar["timestamp"], capsule)

            if order and order.get("side") == "long" and pos == 0:
                stop_dist = price * 0.005
                risk_cap = cash * float(self.cfg["risk"]["RiskPercent"])
                size = max(1, int(risk_cap / max(1e-9, stop_dist)))
                cash -= size * price
                pos = size
                trades.append({"ts": bar["timestamp"], "action": "BUY", "px": price, "size": size})

            elif order and order.get("side") == "flat" and pos != 0:
                cash += pos * price
                trades.append({"ts": bar["timestamp"], "action": "SELL", "px": price, "size": pos})
                pos = 0

            equity_curve.append(cash + pos * price)

        strat.on_finish()

        returns = []
        for i in range(1, len(equity_curve)):
            prev, cur = equity_curve[i - 1], equity_curve[i]
            returns.append((cur - prev) / prev if prev else 0.0)

        peak = equity_curve[0]
        maxdd = 0.0
        for v in equity_curve:
            if v > peak:
                peak = v
            dd = (peak - v) / peak if peak > 0 else 0.0
            if dd > maxdd:
                maxdd = dd

        metrics = {
            "start_equity": 50_000.0,
            "final_equity": equity_curve[-1],
            "num_trades": len([t for t in trades if t["action"] == "BUY"]),
            "sharpe": _sharpe(returns),
            "max_drawdown": maxdd,
        }

        # write blotter
        blotter_path = out / "trades_blotter.csv"
        with open(blotter_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["ts", "action", "px", "size"])
            w.writeheader()
            for t in trades:
                w.writerow(t)

        verdict = "P≠NP (claim)" if collapse_hits > 0 else "OPEN"
        sdk_root = Path(__file__).resolve().parents[2]
        sample_csv = sdk_root / "data/sample.csv"

        capsule = {
            "schema_version": "capsule-1.1.0",
            "created_utc": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "data_source": "in-memory",
            "data_sha256": sha256_file(sample_csv) if sample_csv.exists() else "",
            "params": self.cfg,
            "verdict": verdict,
            "evidence": {"collapse_hits": collapse_hits},
            "metrics": metrics,
        }
        capsule_path = out / "proof_capsule.json"
        capsule_path.write_text(json.dumps(capsule, indent=2))

        (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
        (out / "summary.txt").write_text(make_day_summary(metrics, pb.stats(), verdict))

        pb.close()
        return {
            "blotter": str(blotter_path),
            "capsule": str(capsule_path),
            "metrics": str(out / "metrics.json"),
            "summary": str(out / "summary.txt"),
        }
