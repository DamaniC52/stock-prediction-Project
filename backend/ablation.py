"""Does training breadth actually help, or was it the reframed target?

The switch to pooled training changed two things at once — the prediction target
(price to return) and the amount of data (1 ticker to 503). This isolates the
second: the test set is held fixed at every ticker after the cutoff, and only the
number of tickers contributing training rows varies.

Run:  python ablation.py   (a few minutes; re-downloads price history)
"""

import math

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from features import FEATURE_NAMES, TARGET, build_features
from train import TEST_FRACTION, fetch_price_history, fetch_sp500_tickers

SIZES = [1, 5, 25, 100, 503]
MIN_ROWS_PER_TICKER = 60


def main():
    print("Fetching tickers and history (downloaded once, reused for every size)...")
    frames = fetch_price_history(fetch_sp500_tickers())

    featured = {}
    for ticker, history in frames.items():
        data = build_features(history)
        if len(data) > MIN_ROWS_PER_TICKER:
            featured[ticker] = data

    ordered = sorted(featured)
    all_rows = pd.concat([featured[t] for t in ordered]).sort_index()

    dates = all_rows.index.unique().sort_values()
    cutoff = dates[int(len(dates) * (1 - TEST_FRACTION))]

    # Fixed across every row of the table: only training data varies.
    test = all_rows[all_rows.index >= cutoff]
    standard_error = math.sqrt(0.25 / len(test))

    print(
        f"\nfixed test set: {len(test):,} rows across {len(ordered)} tickers, "
        f"after {cutoff.date()}"
    )
    print(f"standard error at this sample size: {standard_error * 100:.3f}%\n")

    header = (
        f"{'tickers':>8} {'train rows':>12} {'dir acc':>9} {'z vs 50%':>9} "
        f"{'model MAE':>11} {'base MAE':>10}"
    )
    print(header)
    print("-" * len(header))

    baseline_mae = mean_absolute_error(
        test["close"] * (1 + test[TARGET]), test["close"]
    )

    for size in SIZES:
        subset = ordered[:size]
        train = pd.concat([featured[t] for t in subset])
        train = train[train.index < cutoff]

        if len(train) < 50:
            continue

        model = LinearRegression().fit(train[FEATURE_NAMES], train[TARGET])
        predicted_return = model.predict(test[FEATURE_NAMES])

        accuracy = ((predicted_return > 0) == (test[TARGET] > 0)).mean()
        z = (accuracy - 0.5) / standard_error
        mae = mean_absolute_error(
            test["close"] * (1 + test[TARGET]),
            test["close"] * (1 + predicted_return),
        )

        print(
            f"{size:>8} {len(train):>12,} {accuracy * 100:>8.2f}% {z:>9.2f} "
            f"{mae:>10.4f} {baseline_mae:>10.4f}"
        )


if __name__ == "__main__":
    main()
