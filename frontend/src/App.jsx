import { useState } from "react";
import PriceChart from "./PriceChart";
import "./App.css";

const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/+$/, "");

function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  return (
    <div className="app">
      <h1>Stock Price Predictor</h1>
      <p className="subtitle">
        Linear regression on moving averages. Class project &mdash; not
        financial advice.
      </p>

      <form onSubmit={handlePredict}>
        <input
          value={ticker}
          onChange={(event) => setTicker(event.target.value.toUpperCase())}
          placeholder="Ticker, e.g. AAPL"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <div className="stats">
            <div className="stat">
              <span className="stat-label">Predicted next close</span>
              <span className="stat-value">
                ${result.predicted_next_close.toFixed(2)}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Model error (MAE)</span>
              <span className="stat-value">${result.mae.toFixed(2)}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Naive baseline (MAE)</span>
              <span className="stat-value">${result.baseline_mae.toFixed(2)}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Direction accuracy</span>
              <span className="stat-value">
                {(result.direction_accuracy * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          <p className="note">
            The naive baseline predicts tomorrow&rsquo;s close equals
            today&rsquo;s. Direction accuracy is how often the model called
            up-vs-down correctly &mdash; 50% is a coin flip.
          </p>

          <div className="chart-wrap">
            <PriceChart
              dates={result.dates}
              actual={result.actual}
              predicted={result.predicted}
            />
          </div>
        </>
      )}
    </div>
  );
}

export default App;
