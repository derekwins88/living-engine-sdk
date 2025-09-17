"""Living Engine SDK public API."""

from .backtest_runner import BacktestRunner
from .entropy import RegimeName, RegimeResult, classify_regime
from .imm_core import ImmCore
from .narrative import make_day_summary
from .proofbridge import ProofBridge, sha256_file
from .strategy_api import StrategyBase

__all__ = [
    "BacktestRunner",
    "ImmCore",
    "ProofBridge",
    "RegimeName",
    "RegimeResult",
    "StrategyBase",
    "classify_regime",
    "make_day_summary",
    "sha256_file",
]

__version__ = "0.1.0"
