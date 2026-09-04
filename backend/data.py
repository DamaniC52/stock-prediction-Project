import yfinance as yf


def fetch_data(ticker, period="2y"):
    df = yf.download(ticker, period=period, multi_level_index=False)
    df = df.dropna()
    return df


if __name__ == "__main__":
    df = fetch_data("AAPL")
    print(df.head())
    print(df.columns)
    print(len(df), "rows")
