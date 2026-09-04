import { useState } from "react";
import PriceChart from "./PriceChart";
import DataTable from "./DataTable";
import "./App.css";

const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/+$/, "");

function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [view, setView] = useState("chart");

  async function handlePredict(event) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/predict?ticker=${ticker}`);
      const body = await response.json();

      if (!response.ok) {
        throw new Error(body.detail || "Request failed");
      }

      setResult(body);
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  const beatsBaseline = result && result.mae < result.baseline_mae;

  return (
    <div className="app">
      <header className="header">
        <h1>Stock Price Predictor</h1>
        <p className="subtitle">
          Linear regression on moving averages, benchmarked against a naive
          baseline.
        </p>
      </header>

      <form className="search" onSubmit={handlePredict}>
        <input
          value={ticker}
          onChange={(event) => setTicker(event.target.value.toUpperCase())}
          placeholder="Ticker, e.g. AAPL"
          aria-label="Stock ticker symbol"
          spellCheck="false"
        />
        <button type="submit" disabled={loading || !ticker.trim()}>
          {loading ? "Predicting…" : "Predict"}
        </button>
      </form>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {result && (
        <div className={loading ? "results is-stale" : "results"}>
          <section className="stats" aria-label="Model results">
            <div className="stat stat-primary">
              <span className="stat-label">Predicted next close</span>
              <span className="stat-value">
                ${result.predicted_next_close.toFixed(2)}
              </span>
              <span className="stat-note">{result.ticker}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Model error</span>
              <span className="stat-value">${result.mae.toFixed(2)}</span>
              <span className="stat-note">mean absolute error</span>
            </div>
            <div className="stat">
              <span className="stat-label">Naive baseline</span>
              <span className="stat-value">
                ${result.baseline_mae.toFixed(2)}
              </span>
              <span className="stat-note">tomorrow = today</span>
            </div>
            <div className="stat">
              <span className="stat-label">Direction accuracy</span>
              <span className="stat-value">
                {(result.direction_accuracy * 100).toFixed(1)}%
              </span>
              <span className="stat-note">50% is a coin flip</span>
            </div>
          </section>

          <p className={beatsBaseline ? "verdict good" : "verdict bad"}>
            <span className="dot" aria-hidden="true" />
            {beatsBaseline
              ? "The model beats the naive baseline on this ticker."
              : "The naive baseline beats the model — next-day price is dominated by today's price."}
          </p>

          <section className="card">
            <div className="card-head">
              <h2>Actual vs predicted</h2>
              <div className="toggle" role="group" aria-label="View mode">
                <button
                  type="button"
                  className={view === "chart" ? "is-active" : ""}
                  onClick={() => setView("chart")}
                >
                  Chart
                </button>
                <button
                  type="button"
                  className={view === "table" ? "is-active" : ""}
                  onClick={() => setView("table")}
                >
                  Table
                </button>
              </div>
            </div>

            {view === "chart" ? (
              <div className="chart-wrap">
                <PriceChart
                  dates={result.dates}
                  actual={result.actual}
                  predicted={result.predicted}
                />
              </div>
            ) : (
              <DataTable
                dates={result.dates}
                actual={result.actual}
                predicted={result.predicted}
              />
            )}

            <p className="caption">
              {result.dates.length} trading days the model never saw during
              training.
            </p>
          </section>
        </div>
      )}

      <footer className="footer">
        Predictions are statistical estimates, not financial advice.
      </footer>
    </div>
  );
}

export default App;
