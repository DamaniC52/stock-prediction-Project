import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import app
from model import build_features, train_and_predict


@pytest.fixture
def fake_prices():
    """60 days of synthetic prices, so tests never touch the network."""
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    closes = np.linspace(100, 130, 60) + np.sin(np.arange(60)) * 2
    return pd.DataFrame({"Close": closes}, index=dates)


def test_build_features_has_no_missing_values(fake_prices):
    features = build_features(fake_prices)
    assert not features.isna().any().any()


def test_build_features_drops_warmup_and_final_rows(fake_prices):
    # 9 rows lost to the 10-day moving average warm-up, 1 to the shifted target.
    features = build_features(fake_prices)
    assert len(features) == len(fake_prices) - 10


def test_target_is_next_days_close(fake_prices):
    features = build_features(fake_prices)
    first = features.iloc[0]
    next_day_close = fake_prices["Close"].loc[features.index[1]]
    assert first["target"] == pytest.approx(next_day_close)


def test_split_is_chronological_not_shuffled(fake_prices):
    # Guards against the data-leakage mistake of shuffling time series data.
    features = build_features(fake_prices)
    split = int(len(features) * 0.8)
    assert features.index[:split].max() < features.index[split:].min()


def test_metrics_are_in_valid_ranges(fake_prices):
    result = train_and_predict(fake_prices)
    assert 0.0 <= result["direction_accuracy"] <= 1.0
    assert result["mae"] > 0
    assert result["baseline_mae"] > 0
    assert len(result["dates"]) == len(result["actual"]) == len(result["predicted"])


def test_unknown_ticker_returns_404():
    client = TestClient(app)
    response = client.get("/predict", params={"ticker": "NOTAREALTICKER"})
    assert response.status_code == 404
