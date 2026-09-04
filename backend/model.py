import os

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error

from data import fetch_data
from features import FEATURE_NAMES, TARGET, build_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

_bundle = joblib.load(MODEL_PATH)
MODEL = _bundle["model"]
TRAINED_THROUGH = pd.Timestamp(_bundle["trained_through"])
TRAINING_METRICS = _bundle["metrics"]
TICKERS_TRAINED = _bundle["tickers_trained"]


def predict_for(df):
    """Score one ticker with the model trained across the whole index.

    Only dates after the training cutoff are reported, so the numbers shown are
    always out-of-sample for this stock.
    """
    data = build_features(df)
    if data.empty:
        return None

    predicted_return = MODEL.predict(data[FEATURE_NAMES])
    close = data["close"]

    evaluated = pd.DataFrame(
        {
            "actual": close * (1 + data[TARGET]),
            "predicted": close * (1 + predicted_return),
            "close": close,
            "predicted_return": predicted_return,
            "actual_return": data[TARGET],
        },
        index=data.index,
    )

    out_of_sample = evaluated[evaluated.index > TRAINED_THROUGH]
    if len(out_of_sample) < 5:
        out_of_sample = evaluated.tail(60)

    latest = data.iloc[[-1]]
    next_return = float(MODEL.predict(latest[FEATURE_NAMES])[0])
    next_close = float(latest["close"].iloc[0] * (1 + next_return))

    return {
        "predicted_next_close": next_close,
        "predicted_next_return": next_return,
        "mae": float(
            mean_absolute_error(out_of_sample["actual"], out_of_sample["predicted"])
        ),
        "baseline_mae": float(
            mean_absolute_error(out_of_sample["actual"], out_of_sample["close"])
        ),
        "direction_accuracy": float(
            (
                (out_of_sample["predicted_return"] > 0)
                == (out_of_sample["actual_return"] > 0)
            ).mean()
        ),
        "dates": [d.strftime("%Y-%m-%d") for d in out_of_sample.index],
        "actual": [float(v) for v in out_of_sample["actual"]],
        "predicted": [float(v) for v in out_of_sample["predicted"]],
        "trained_on_tickers": TICKERS_TRAINED,
        "trained_through": str(TRAINED_THROUGH.date()),
        "training_direction_accuracy": TRAINING_METRICS["direction_accuracy"],
    }


if __name__ == "__main__":
    result = predict_for(fetch_data("AAPL"))
    print("Predicted next close:  $", round(result["predicted_next_close"], 2))
    print("Predicted next return: ", f"{result['predicted_next_return'] * 100:+.3f}%")
    print("Model MAE:             $", round(result["mae"], 2))
    print("Baseline MAE:          $", round(result["baseline_mae"], 2))
    print("Direction accuracy:    ", f"{result['direction_accuracy'] * 100:.1f}%")
    print("Out-of-sample days:    ", len(result["dates"]))
