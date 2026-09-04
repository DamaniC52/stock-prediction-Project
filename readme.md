# Stock Price Predictor

A next-day stock movement predictor trained across all 503 S&P 500 constituents with scikit-learn, served over a FastAPI REST API, with a React frontend. Enter a ticker, get a prediction and a chart of how the model performed on dates it never trained on.

**The interesting part isn't the prediction — it's the evaluation.** Every result is benchmarked against a naive baseline and tested for statistical significance. See [Results](#results).

<!-- Add a screenshot once deployed:
![Screenshot](docs/screenshot.png)
-->

**Live demo:** https://frontend-pi-six-55.vercel.app
**API docs:** https://stock-prediction-project-q5io.onrender.com/docs

The API runs on a free tier that sleeps when idle, so the first request after a quiet period may take up to a minute to wake it.

---

## Stack

| Layer | Technology |
|---|---|
| Data | yfinance (Yahoo Finance historical prices) |
| Processing | pandas |
| Model | scikit-learn — LinearRegression, persisted with joblib |
| API | FastAPI + uvicorn |
| Frontend | React (Vite) + Chart.js |
| Tests | pytest |

## How it works

**Predict returns, not price.** The target is tomorrow's *percentage change*, not tomorrow's dollar close. This matters: consecutive prices are so highly correlated that a model predicting "tomorrow ≈ today" scores well on dollar error while learning nothing. Predicting the change removes that free ride and forces the model to address the part that is actually unknown. (An earlier version predicted price directly and lost to the naive baseline — see [What changed](#what-changed).)

**Features are all scale-free** — returns over 1/5/10 days, gaps between price and its moving averages, realized volatility, and relative volume. Because none of them is a dollar amount, a $500 stock and a $20 stock produce comparable rows, which is what makes it valid to train one model across the entire index. A unit test enforces this property.

**Trained across the S&P 500.** 503 tickers, ~241,000 daily observations, rather than one stock's ~500 rows.

**Training is offline; serving loads the result.** `train.py` fits the model and writes `model.joblib`; the API loads that artifact at startup and only runs inference per request. Training inside the request would take minutes and exceed the host's memory.

**The split is chronological, not random** — every training row predates every test row (cutoff 2026-04-16). Shuffling time series lets a model learn from the future and produces scores that look excellent and mean nothing.

## Results

Pooled across 503 tickers, 48,181 test observations on dates after the training cutoff:

| Metric | Value |
|---|---|
| Direction accuracy | **50.96%** |
| 95% confidence interval | 50.52% – 51.41% |
| z-score vs. a coin flip | 4.22 |
| Model MAE | $4.4434 |
| Naive baseline MAE | $4.4409 |

**The direction signal is small but statistically real.** At 4.2 standard errors above 50%, the confidence interval excludes a coin flip. That is a genuine finding — and it is also almost exactly what published research reports for daily equity direction, which is the reason to believe it rather than doubt it.

**It is not, however, worth money.** A ~1% edge is far below realistic transaction costs. Dollar-error MAE remains a statistical tie with the baseline, which is expected: MAE on price level is dominated by the level itself and is a poor instrument for detecting a small directional edge.

The most interpretable coefficient is `ma5_gap` at **-0.033** — when a stock sits above its 5-day average, the model expects a slightly negative next-day return. That is short-horizon mean reversion, a documented effect, and the model found it independently.

### A caveat worth stating

Run this on a single ticker and you may see something like 56.8% direction accuracy on ~95 days. **That number is not meaningful.** With 95 samples the standard error is ~5.1%, so 56.8% sits about 1.3 standard errors from chance — comfortably inside noise. The pooled 50.96% across 48,181 observations is the number to trust. Sample size is what separates a result from a coincidence, and a single-stock readout is the easiest way to fool yourself here.

## What changed

The first version predicted tomorrow's **price** from moving averages on a single stock. It scored $4.19 MAE against a naive baseline's $4.04 — it lost to simply assuming no change — with 47.5% direction accuracy on 99 days.

Diagnosing *why* drove every change since: the target was wrong (price, not return), the features were three restatements of the same information, and the sample was far too small to measure anything. Fixing all three moved direction accuracy from an unmeasurable 47.5% to a statistically significant 50.96%.

## Running locally

Two servers, two terminals.

**Backend** (from `backend/`):

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

The API runs at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

**Frontend** (from `frontend/`):

```bash
npm install
npm run dev
```

Open `http://localhost:5173`.

## Tests

```bash
cd backend
pytest
```

Covers feature construction, that the split stays chronological, metric ranges, and the API's 404 path for unknown tickers.

## Project structure

```
backend/
  features.py    scale-free feature engineering (shared by training and serving)
  train.py       offline: downloads the S&P 500, trains, writes model.joblib
  model.joblib   the trained model artifact
  data.py        fetch and clean prices from yfinance
  model.py       loads the artifact, scores a single ticker
  app.py         FastAPI app exposing GET /predict
  test_model.py  pytest suite
frontend/
  src/App.jsx         ticker input, stat tiles, data fetching
  src/PriceChart.jsx  Chart.js line chart of actual vs predicted
  src/DataTable.jsx   table view of the same data
  src/useChartTheme.js  light/dark chart palette
```

`features.py` is imported by both `train.py` and `model.py` on purpose — if training and serving computed features differently, predictions would be wrong in a way nothing would catch.

## Retraining

```bash
cd backend
python train.py
```

Downloads current S&P 500 constituents from Wikipedia, pulls two years of history for each, and overwrites `model.joblib`. Takes a few minutes.

## Possible extensions

- Predict returns or direction directly instead of absolute price
- Add features with a plausible basis: volume trends, volatility, RSI
- Walk-forward validation instead of a single split
- Compare against a model class that can capture non-linearity, with the baseline still reported

---

*Built as a CS project. Not financial advice.*
