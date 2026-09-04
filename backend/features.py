import pandas as pd

FEATURE_NAMES = [
    "ret_1",
    "ret_5",
    "ret_10",
    "ma5_gap",
    "ma10_gap",
    "volatility",
    "volume_ratio",
]

TARGET = "next_return"


def build_features(df):
    """Scale-free features so one model can pool many stocks.

    Every column is a ratio or percentage change, never a dollar amount — a $500
    stock and a $20 stock produce comparable rows, which is what makes training
    across the whole index possible.
    """
    close = df["Close"]
    daily_return = close.pct_change()

    data = pd.DataFrame(index=df.index)
    data["ret_1"] = daily_return
    data["ret_5"] = close.pct_change(5)
    data["ret_10"] = close.pct_change(10)
    data["ma5_gap"] = close / close.rolling(5).mean() - 1
    data["ma10_gap"] = close / close.rolling(10).mean() - 1
    data["volatility"] = daily_return.rolling(10).std()

    if "Volume" in df:
        data["volume_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean() - 1
    else:
        data["volume_ratio"] = 0.0

    data[TARGET] = daily_return.shift(-1)
    data["close"] = close

    return data.replace([float("inf"), float("-inf")], pd.NA).dropna()
