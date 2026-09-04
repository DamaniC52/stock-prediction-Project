# Stock Price Predictor

A next-day stock price predictor built with scikit-learn, served over a FastAPI REST API, with a React frontend. Enter a ticker, get a prediction and a chart of how the model performed on unseen data.

**The interesting part isn't the prediction — it's the evaluation.** The model is benchmarked against a naive baseline, and it loses. See [Results](#results).

<!-- Add a screenshot once deployed:
![Screenshot](docs/screenshot.png)
-->

**Live demo:** _(add Vercel URL)_
The API is hosted on a free tier that sleeps when idle, so the first request may take up to a minute to wake it.

---

## Stack

| Layer | Technology |
|---|---|
| Data | yfinance (Yahoo Finance historical prices) |
| Processing | pandas |
| Model | scikit-learn — LinearRegression |
| API | FastAPI + uvicorn |
| Frontend | React (Vite) + Chart.js |
| Tests | pytest |

## How it works

**Features.** For each trading day the model sees three inputs: the current close, the 5-day moving average, and the 10-day moving average. The label is the *next* day's close, produced with `Close.shift(-1)`.

**Train/test split.** The split is chronological — the first 80% of days train, the most recent 20% test. It is deliberately **not** shuffled. Shuffling time series data lets the model train on future data and be tested on the past, which leaks information and produces scores that look excellent and mean nothing.

**Evaluation.** Three numbers are reported:

- **Model MAE** — average error in dollars on the test set.
- **Baseline MAE** — the same metric for a naive predictor that says *tomorrow's close equals today's*.
- **Direction accuracy** — how often the model correctly called up vs. down. 50% is a coin flip.

## Results

Two years of AAPL data, 99 test days:

| Metric | Value |
|---|---|
| Model MAE | $4.19 |
| Naive baseline MAE | **$4.04** |
| Direction accuracy | 47.5% |

**The naive baseline beats the model, and direction accuracy is slightly worse than a coin flip.**

This is the finding worth reporting, not hiding. Reading MAE alone, $4.19 on a ~$320 stock looks like a 1.3% error and seems good. The baseline shows why that is an illusion: day-to-day price changes are small, so *any* model that outputs something close to today's price scores well on MAE. The regression is essentially learning "tomorrow ≈ today," and adding moving averages makes it marginally worse than just saying so outright.

What this actually demonstrates:

1. **Absolute price is the wrong prediction target.** Because consecutive prices are highly correlated, a price-level metric flatters a model that has learned nothing useful. Predicting *returns* or *direction* is the meaningful framing.
2. **A metric without a baseline is not a result.** Any error number needs something to compare against before it means anything.
3. **Sub-50% direction accuracy on ~99 samples is not evidence of an anti-signal** — it's within the range of noise. Claiming a tradeable inverse signal here would be overfitting to a small test set.

Beating a persistence baseline on daily equity prices with three moving-average features is not a realistic goal; efficient-market behavior means most of tomorrow's move is genuinely unpredictable from yesterday's price alone. The value of the project is in measuring that honestly rather than reporting a flattering number.

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
  data.py        fetch and clean prices from yfinance
  model.py       feature engineering, training, evaluation
  app.py         FastAPI app exposing GET /predict
  test_model.py  pytest suite
frontend/
  src/App.jsx        ticker input, stats, data fetching
  src/PriceChart.jsx Chart.js line chart of actual vs predicted
```

## Possible extensions

- Predict returns or direction directly instead of absolute price
- Add features with a plausible basis: volume trends, volatility, RSI
- Walk-forward validation instead of a single split
- Compare against a model class that can capture non-linearity, with the baseline still reported

---

*Built as a CS coursework project. Not financial advice.*
