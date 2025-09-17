"""Tests for the entropy classification helper."""

import math

import pytest

from living_engine.entropy import RegimeResult, classify_regime


@pytest.mark.parametrize(
    "entropy,expected_regime",
    [
        (0.01, "P-like"),
        (0.05, "NP-drift"),
        (0.11, "collapse"),
    ],
)
def test_classify_regime(entropy: float, expected_regime: str) -> None:
    result: RegimeResult = classify_regime(entropy, 0.045, 0.09, 0.1)
    assert result["regime"] == expected_regime
    assert math.isclose(result["entropy"], entropy)
    assert result["glyph"]


def test_np_regime_between_thresholds() -> None:
    result = classify_regime(0.095, 0.045, 0.09, 0.2)
    assert result["regime"] == "NP"


def test_invalid_thresholds_raise() -> None:
    with pytest.raises(ValueError):
        classify_regime(0.1, 0.09, 0.05, 0.2)


def test_negative_entropy_rejected() -> None:
    with pytest.raises(ValueError):
        classify_regime(-0.01, 0.01, 0.02, 0.03)
