"""Offline training across the S&P 500.

Run this by hand when you want to retrain:  python train.py
It writes model.joblib, which the API loads at startup.
"""

import io

import joblib
import numpy as np
import pandas as pd
import requests
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from features import FEATURE_NAMES, TARGET, build_features

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
MODEL_PATH = "model.joblib"
CHUNK_SIZE = 50
TEST_FRACTION = 0.2


def fetch_sp500_tickers():
    response = requests.get(
        WIKI_URL, headers={"User-Agent": "Mozilla/5.0 (student project)"}, timeout=30
    )
    response.raise_for_status()
    table = pd.read_html(io.StringIO(response.text))[0]
    # BRK.B is BRK-B in Yahoo's notation.
    return [symbol.replace(".", "-") for symbol in table["Symbol"]]


def fetch_price_history(tickers, period="2y"):
    frames = {}

    for start in range(0, len(tickers), CHUNK_SIZE):
        chunk = tickers[start : start + CHUNK_SIZE]
        print(f"  downloading {start + 1}-{start + len(chunk)} of {len(tickers)}")

        raw = yf.download(
            chunk, period=period, group_by="ticker", progress=False, threads=True
        )

        for ticker in chunk:
            if ticker not in raw.columns.get_level_values(0):
                continue
            history = raw[ticker].dropna()
            if len(history) > 40:
                frames[ticker] = history

    return frames


def build_training_set(frames):
    rows = []
    for ticker, history in frames.items():
        featured = build_features(history)
        featured["ticker"] = ticker
        rows.append(featured)

    combined = pd.concat(rows)
    return combined.sort_index()


def evaluate(model, X_test, y_test, close_test):
    predicted_return = model.predict(X_test)

    # Convert both back to dollars so the number stays interpretable.
    predicted_price = close_test * (1 + predicted_return)
    actual_price = close_test * (1 + y_test)

    return {
        "mae": mean_absolute_error(actual_price, predicted_price),
        "baseline_mae": mean_absolute_error(actual_price, close_test),
        "direction_accuracy": float(
            ((predicted_return > 0) == (y_test > 0)).mean()
        ),
        "test_rows": int(len(y_test)),
    }


def main():
    print("Fetching S&P 500 constituents...")
    tickers = fetch_sp500_tickers()
    print(f"  {len(tickers)} tickers")

    print("Downloading price history (this takes a few minutes)...")
    frames = fetch_price_history(tickers)
    print(f"  usable history for {len(frames)} tickers")

    print("Building features...")
    data = build_training_set(frames)
    print(f"  {len(data):,} rows")

    # Split on the calendar, not at random: every training row must predate every
    # test row, or the model learns from the future.
    dates = data.index.unique().sort_values()
    cutoff = dates[int(len(dates) * (1 - TEST_FRACTION))]
    train = data[data.index < cutoff]
    test = data[data.index >= cutoff]
    print(f"  train {len(train):,} rows  |  test {len(test):,} rows  |  cutoff {cutoff.date()}")

    model = LinearRegression()
    model.fit(train[FEATURE_NAMES], train[TARGET])

    metrics = evaluate(
        model, test[FEATURE_NAMES], test[TARGET], test["close"]
    )

    print("\nResults on unseen dates, pooled across the index")
    print(f"  Model MAE:          ${metrics['mae']:.2f}")
    print(f"  Baseline MAE:       ${metrics['baseline_mae']:.2f}")
    print(f"  Direction accuracy: {metrics['direction_accuracy'] * 100:.2f}%")
    print(f"  Test rows:          {metrics['test_rows']:,}")

    print("\nLearned coefficients")
    for name, weight in zip(FEATURE_NAMES, model.coef_):
        print(f"  {name:>13}: {weight:+.5f}")

    joblib.dump(
        {
            "model": model,
            "features": FEATURE_NAMES,
            "metrics": metrics,
            "tickers_trained": len(frames),
            "trained_through": str(cutoff.date()),
        },
        MODEL_PATH,
    )
    print(f"\nSaved {MODEL_PATH}")


if __name__ == "__main__":
    main()
