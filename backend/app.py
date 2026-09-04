import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data import fetch_data
from model import predict_for

app = FastAPI(title="Stock Predictor API")

allowed_origins = ["http://localhost:5173"]
if os.environ.get("FRONTEND_URL"):
    allowed_origins.append(os.environ["FRONTEND_URL"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "Stock Predictor API",
        "docs": "/docs",
        "example": "/predict?ticker=AAPL",
    }


@app.get("/predict")
def predict(ticker: str = "AAPL"):
    df = fetch_data(ticker)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for '{ticker}'")

    result = predict_for(df)

    if result is None:
        raise HTTPException(
            status_code=422, detail=f"Not enough price history for '{ticker}'"
        )

    result["ticker"] = ticker.upper()
    return result
