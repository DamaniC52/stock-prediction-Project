import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from data import fetch_data


def build_features(df):
    data = pd.DataFrame(index=df.index)
    data["prev_close"] = df["Close"]
    data["ma5"] = df["Close"].rolling(5).mean()
    data["ma10"] = df["Close"].rolling(10).mean()
    data["target"] = df["Close"].shift(-1)
    return data.dropna()


def train_and_predict(df):
    data = build_features(df) 

    X = data[["prev_close", "ma5", "ma10"]]
    y = data["target"]

    split = int(len(data) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)

    # Naive baseline: assume tomorrow's close equals today's. The model is only
    # worth anything if it beats this.
    baseline = X_test["prev_close"]
    baseline_mae = mean_absolute_error(y_test, baseline)

    actual_up = y_test.values > baseline.values
    predicted_up = predictions > baseline.values
    direction_accuracy = (actual_up == predicted_up).mean()

    next_close = model.predict(X.tail(1))[0]

    return {
        "predicted_next_close": float(next_close),
        "mae": float(mae),
        "baseline_mae": float(baseline_mae),
        "direction_accuracy": float(direction_accuracy),
        "dates": [d.strftime("%Y-%m-%d") for d in X_test.index],
        "actual": [float(v) for v in y_test],
        "predicted": [float(v) for v in predictions],
    }


if __name__ == "__main__":
    df = fetch_data("AAPL")
    result = train_and_predict(df)
    print("Predicted next close: $", round(result["predicted_next_close"], 2))
    print("Model MAE:            $", round(result["mae"], 2))
    print("Baseline MAE:         $", round(result["baseline_mae"], 2))
    print("Direction accuracy:   ", round(result["direction_accuracy"] * 100, 1), "%")
    print("Test days:", len(result["dates"]))
