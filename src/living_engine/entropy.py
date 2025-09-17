"""Entropy regime classification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

RegimeName = Literal["P-like", "NP-drift", "NP", "collapse"]


class RegimeResult(TypedDict):
    """Structured result for :func:`classify_regime`."""

    regime: RegimeName
    glyph: str
    entropy: float


@dataclass(frozen=True)
class _RegimeThresholds:
    p_threshold: float
    np_threshold: float
    collapse_threshold: float

    def __post_init__(self) -> None:  # noqa: D401 - short validation helper
        if self.p_threshold < 0 or self.np_threshold < 0 or self.collapse_threshold < 0:
            raise ValueError("Thresholds must be non-negative.")
        if self.p_threshold > self.np_threshold:
            raise ValueError("P threshold must be less than or equal to NP threshold.")
        if self.np_threshold > self.collapse_threshold:
            raise ValueError("NP threshold must be less than or equal to collapse threshold.")


_GLYPHS: dict[RegimeName, str] = {
    "P-like": "⥁",
    "NP-drift": "⟲",
    "NP": "⟲",
    "collapse": "⧖",
}


def classify_regime(
    entropy: float,
    p_threshold: float,
    np_threshold: float,
    collapse_threshold: float,
) -> RegimeResult:
    """Classify entropy into a symbolic regime.

    Parameters
    ----------
    entropy:
        Scalar entropy value for the current observation. Must be finite and non-negative.
    p_threshold, np_threshold, collapse_threshold:
        Regime thresholds. They must be monotonic (``p <= np <= collapse``).

    Returns
    -------
    RegimeResult
        Dictionary containing the resolved regime name, glyph, and echoing the input entropy.

    Raises
    ------
    ValueError
        If thresholds are inconsistent or ``entropy`` is negative.
    """

    thresholds = _RegimeThresholds(p_threshold, np_threshold, collapse_threshold)

    if entropy < 0:
        raise ValueError("Entropy must be non-negative.")

    if entropy >= thresholds.collapse_threshold:
        regime: RegimeName = "collapse"
    elif entropy < thresholds.p_threshold:
        regime = "P-like"
    elif entropy < thresholds.np_threshold:
        regime = "NP-drift"
    else:
        regime = "NP"

    return RegimeResult(regime=regime, glyph=_GLYPHS[regime], entropy=float(entropy))


__all__ = ["RegimeName", "RegimeResult", "classify_regime"]
