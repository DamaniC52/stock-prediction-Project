import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import app
from features import FEATURE_NAMES, TARGET, build_features
from model import predict_for


@pytest.fixture
def fake_prices():
    """Synthetic prices, so tests never depend on the network."""
    dates = pd.date_range("2024-01-01", periods=400, freq="D")
    closes = np.linspace(100, 130, 400) + np.sin(np.arange(400)) * 2
    volume = np.full(400, 1_000_000.0)
    return pd.DataFrame({"Close": closes, "Volume": volume}, index=dates)


def test_features_have_no_missing_values(fake_prices):
    data = build_features(fake_prices)
    assert not data.isna().any().any()


def test_features_are_scale_free(fake_prices):
    """A 10x more expensive stock must produce near-identical features.

    This is what lets one model pool 500 stocks; if it breaks, pooled training
    is silently invalid.
    """
    cheap = build_features(fake_prices)
    expensive = build_features(fake_prices.assign(Close=fake_prices["Close"] * 10))

    for column in FEATURE_NAMES:
        assert np.allclose(cheap[column], expensive[column])


def test_target_is_next_day_return(fake_prices):
    data = build_features(fake_prices)
    first = data.iloc[0]
    next_close = fake_prices["Close"].loc[data.index[1]]
    expected = next_close / first["close"] - 1
    assert first[TARGET] == pytest.approx(expected)


def test_prediction_metrics_are_in_valid_ranges(fake_prices):
    result = predict_for(fake_prices)
    assert 0.0 <= result["direction_accuracy"] <= 1.0
    assert result["mae"] > 0
    assert result["baseline_mae"] > 0
    assert len(result["dates"]) == len(result["actual"]) == len(result["predicted"])


def test_too_little_history_returns_none():
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    tiny = pd.DataFrame(
        {"Close": [10, 11, 12, 11, 10.5], "Volume": [1e6] * 5}, index=dates
    )
    assert predict_for(tiny) is None


def test_unknown_ticker_returns_404():
    client = TestClient(app)
    response = client.get("/predict", params={"ticker": "NOTAREALTICKER"})
    assert response.status_code == 404
